from django_redis import get_redis_connection
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .constants import SMS_CODES_TIMES
from celery_tasks.sms.tasks import send_sms_code
# Create your views here.


# sms_codes/mobile
class SMSCodesView(APIView):
    """短信验证码视图类"""
    def get(self, request, mobile):
        # 连接redis
        redis_conn = get_redis_connection('verify_codes')
        # 查询该号码是否注册
        is_have_flag = redis_conn.get('sms_flag_{}'.format(mobile))
        if is_have_flag:
            return Response({'message':'发短信过于频繁'}, status=status.HTTP_400_BAD_REQUEST)
        # 构建随机验证码
        sms_code = '%06d'%random.randint(0,99999)

        pl = redis_conn.pipeline()
        # 添加注册记录
        pl.setex(name='sms_flag_{}'.format(mobile), value=1,time=SMS_CODES_TIMES)
        # 添加该验证码记录
        pl.setex(name='sms_code_{}'.format(mobile), value=sms_code, time=SMS_CODES_TIMES)

        pl.execute()
        # celery异步发短信,云通讯发短信
        send_sms_code.delay(mobile, sms_code, str(SMS_CODES_TIMES))

        return Response({'sms_code':sms_code})


