from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from django_redis import get_redis_connection

from goods.models import SKU
from .models import OrderInfo,OrderGoods

class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class CreateOrderSerializer(serializers.ModelSerializer):
    """创建订单的序列化器"""
    class Meta:
        model = OrderInfo
        fields = ['order_id', 'address', 'pay_method']
        read_only_fields = ['order_id']
        extra_kwgrs= {
            'address':{
                'write_only':True,
                'required':True
            },
            'pay_method':{
                'write_only':True,
                'pay_method':True
            }
        }



    def create(self,validated_data):

        address = validated_data['address']
        pay_method = validated_data['pay_method']
        # 1、获取user对象
        user = self.context['request'].user

        # 使用事物,生成订单
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                # 2、创建order_id
                order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
                # 3、根据Orderinfo创建order对象
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=0,
                    freight = Decimal(10.0),
                    pay_method=pay_method,
                    status = OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                )
                # 4、查询redis获取该用户的勾选sku_id
                redis_conn = get_redis_connection('cart')

                redis_cart = redis_conn.hgetall('cart_{}'.format(user.id))
                chioces = redis_conn.smembers('cart_chioce_{}'.format(user.id))


                cart = {}  # 下单商品的di和数量
                for sku_id in chioces:
                    cart[int(sku_id)] = int(redis_cart[sku_id])

                # 5、查询所有的sku_id
                sku_id_list = cart.keys()
                # 6、便利sku_id，修改该sku的库存销量和对应的spu的销量
                for sku_id in sku_id_list:
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        real_stock = sku.stock  # 进行数据库更新前的库存
                        real_sales = sku.sales
                        count = cart[sku.id]  # 购买的数量

                        if real_stock < count:
                            transaction.savepoint_rollback(save_id)
                            raise serializers.ValidationError('商品库存不足')

                        new_stock = real_stock - count
                        new_sales = real_sales + count
                        # 乐观锁，在进行数据更新的时候对原有的数据进行查询，如果根之前查询的数据一样表示没有其他人进行数据更改，则可以进行数据修改，
                        # 如果数据和之前不一样则表示数据被修改，则不执行数据更新数据的操作，
                        # 乐观锁必须要mysql的事物隔离级别为Read committed 读取已提交
                        ret = SKU.objects.filter(id=sku_id, stock=real_stock, sales=real_sales).update(stock=new_stock, sales=new_sales)

                        if ret == 0:
                            # 如果没有执行数据更新操作，表示数据被修改，再次进行数据的查询之后再来更新数据，直至库存不足
                            continue

                        # 累计商品的SPU 销量信息
                        sku.goods.sales += count
                        sku.goods.save()

                        # 7、完善order对象的total_count和total_amount
                        order.total_count += count
                        order.total_amount += sku.price * count
                        order.save()

                        # 8、保存订单商品,根据OrderGoods创建对象的sku数据
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=count,
                            price=sku.price,
                        )
                        # 当前该sku完成数据更新，跳出循环，进行下一个sku的数据更新
                        break

                    # 总金额加上运费
                    order.total_amount += order.freight
                    order.save()
            except serializers.ValidationError:
                raise
            except Exception:
                raise


            # 9、删除redis中的已下单的sku
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, *chioces)
            pl.srem('cart_chioce_%s' % user.id, *chioces)
            pl.execute()
            # 10、返回order对象
            return order

