from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework import status
import pickle
import base64

from .serializers import CartSerializer
from .serializers import GetCartSerializer
from .serializers import DeleteCartSerializer
from . import constants
from goods.models import SKU
# Create your views here.


class CartView(APIView):

    def perform_authentication(self, request):
        """重写父类的用户验证方法，不在进入视图前就检查JWT"""
        pass

    def get(self,request):
        """获取购物车数据"""
        try:
            user = request.user
        except Exception:
            user = None
        if user is not None and user.is_authenticated:
            """用户登陆就从redis获取数据"""
            redis_conn = get_redis_connection('cart')
            sku_count_dict = redis_conn.hgetall('cart_{}'.format(user.id))
            chioces = redis_conn.smembers('cart_chioce_{}'.format(user.id))
            sku_objs = []
            for sku_id,count in sku_count_dict.items():
                try:
                    sku_obj = SKU.objects.get(id=sku_id)
                except SKU.DoesNotExist:
                    pass
                else:
                    sku_obj.count= count
                    sku_obj.chioce = sku_id in chioces
                    sku_objs.append(sku_obj)

            serializer = GetCartSerializer(sku_objs, many=True)
            return Response(serializer.data)
        else:
            """用户未登录，从cookies获取数据"""
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
                sku_objs = []
                for sku_id,v in cart_dict.items():
                    try:

                        sku_obj = SKU.objects.get(id=sku_id)
                    except SKU.DoesNotExist:
                        pass
                    else:
                        sku_obj.count = cart_dict[sku_id]['count']
                        sku_obj.chioce = cart_dict[sku_id]['chioce']
                        sku_objs.append(sku_obj)
                serializer = GetCartSerializer(sku_objs, many=True)
                return Response(serializer.data)
            else:
                return Response({'data':None})

    def post(self,request):
        """
        添加购物车
        :param request:
        :return:
        """
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        chioce = serializer.validated_data['chioce']
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            """表示已登陆,将购物车的记录添加到redis"""
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            user_id = user.id
            """
            商品的数量和id  数据存储格式 hash
            {
            'cart_user_id':{'sku_id':'count'}
            }
            """
            pl.hincrby('cart_{}'.format(user_id), sku_id, count)
            """
            是否勾选的数据存储 set
            ‘cart_chioce_user_id’：‘sku_id, sku_id, sku_id’
            """
            if chioce:
                pl.sadd('cart_chioce_{}'.format(user_id), sku_id)

            pl.execute()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:

            """
            用户未登陆，将用户记录添加到COOKIES
            数据存储格式
            cart:
            {
                sku_id1:{count:1,chioce:True},
                sku_id2:{count:2,chioce:False}
            }
            """
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                cart_dict ={}


            if sku_id in cart_dict:
                cart_dict[sku_id]['count'] += count

            cart_dict[sku_id]={'count': count,'chioce': chioce}

            # 对cart_dict数据进行处理
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response.set_cookie('cart', cart_data, max_age=constants.CART_COOKIE_EXPIRES)
            return response

    def put(self,request):
        """更新购物车数据"""
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        chioce = serializer.validated_data['chioce']
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            """表示已登陆,redis"""
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            user_id = user.id

            # 设置用户购物车中商品的id和对应数量count hash
            pl.hset('cart_{}'.format(user_id), sku_id, count)

            # 设置用户购物车的勾状态
            if chioce:
                pl.sadd('cart_chioce_{}'.format(user_id), sku_id)
            else:
                # 不勾选
                # srem(name, *values): 从set中移除元素，如果元素不存在，直接忽略
                pl.srem('cart_chioce_{}'.format(user_id), sku_id)

            pl.execute()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            response = Response(serializer.data)
            # 3.2 如果用户未登录，更新cookie中购物车记录
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart is None:
                return response

            cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            if cart_dict is None:
                return response


            if sku_id in cart_dict:

                cart_dict[sku_id] = {'count': count, 'chioce': chioce}

            # 对cart_dict数据进行处理
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response.set_cookie('cart', cart_data, max_age=constants.CART_COOKIE_EXPIRES)
            return response

    def delete(self,request):
        """删除购物车数据"""
        serializer = DeleteCartSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            """表示已登陆,将从redis删除记录"""
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            user_id = user.id

            pl.hdel('cart_{}'.format(user_id), sku_id)

            pl.srem('cart_chioce_{}'.format(user_id), sku_id)

            pl.execute()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            """从cookies删除记录"""
            response = Response(status=status.HTTP_204_NO_CONTENT)
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart is None:
                return response

            cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            if not cart_dict:
                return response

            if sku_id in cart_dict:
                del cart_dict[sku_id]

            cookie_data = base64.b64encode(pickle.dumps(cart_dict)).decode()  # str

            # 设置购物车cookie信息
            response.set_cookie('cart', cookie_data, expires=constants.CART_COOKIE_EXPIRES)

            # 4. 返回应答，status=204
        return response