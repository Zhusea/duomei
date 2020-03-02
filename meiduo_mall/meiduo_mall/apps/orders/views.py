from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection
from rest_framework.response import Response
from decimal import Decimal
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from alipay import Alipay
import os


from goods.models import SKU
from .models import OrderInfo
from .serializers import OrderSettlementSerializer
from .serializers import CreateOrderSerializer
# Create your views here.


class SetOrderView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user = request.user


        user_id = user.id
        redis_conn = get_redis_connection('cart')


        redis_cart = redis_conn.hgetall('cart_{}'.format(user_id))
        chioce = redis_conn.smembers('cart_chioce_{}'.format(user_id))
        cart = {}

        for sku_id,count in redis_cart.items():
            if sku_id in chioce:
                cart[int(sku_id)] = int(count)



        if cart:
            skus = SKU.objects.filter(id__in=cart.keys())

        for sku in skus:
            sku.count = cart[sku.id]

        # 运费
        freight = Decimal('10.00')

        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})

        return Response(serializer.data)


class CreateOrderView(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CreateOrderSerializer


class OrderPayView(APIView):
    """订单支付视图"""
    permission_classes = [IsAuthenticated]
    def get(self,request, order_id):
        user = request.user
        try:
            order = OrderInfo.objects.get(
                order_id=order_id,
                user=user,
                pay_method=OrderInfo.PAY_METHODS_ENUM["ALIPAY"],
                status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"],
            )
        except OrderInfo.DoesNotExist:
            return Response({'meaaage':'订单错误'},status=status.HTTP_400_BAD_REQUEST)

        alipay = Alipay(
            appid="2016100100641406",
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_private_key.pem'),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'alipay_public_key.pem'),
            sign_type="RSA2",
            debug=True
        )

        sum_price = order.total_amount
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(sum_price),
            subject='美多商城',
            return_url='http://www.meiduo.site:8080/pay_success.html',
            notify_url=None  # this is optional
        )
        alipay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string

        return Response({'alipay_url':alipay_url})


class PaymentStatusView(APIView):
    """支付订单状态校验"""

    def put(self, request):
        data = request.query_params.dict()
        signature = data.pop("sign")

        alipay = Alipay(
            appid="2016100100641406",
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_private_key.pem'),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alipay_public_key.pem'),
            sign_type="RSA2",
            debug=True
        )

        success = alipay.verify(data, signature)

        if not success:
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)

        # 获取订单编号和支付宝流水号
        order_id = data.get('out_trade_no')
        trade_id = data.get('trade_no')

        # 校验订单id(order_id)
        try:
            order = OrderInfo.objects.get(
                order_id=order_id,
                user=request.user,
                status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']
            )
        except OrderInfo.DoesNotExist:
            return Response({'message': '订单信息有误'}, status=status.HTTP_400_BAD_REQUEST)



        # 更新订单的支付状态
        order.status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        order.save()

        return Response({'trade_id': trade_id})