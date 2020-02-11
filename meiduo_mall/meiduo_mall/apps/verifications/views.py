from django.shortcuts import render
from django.shortcuts import HttpResponse
from django_redis import get_redis_connection
from rest_framework.views import APIView
from meiduo_mall.libs.yuntongxun.sms import CCP
import random

from .constants import SMS_CODES_TIMES
from .constants import SMS_CODE_TEMP_ID
# Create your views here.


# sms_codes/mobile
class SMSCodesView(APIView):
    """短信验证码视图类"""
    def get(self, request, mobile):
        redis_conn = get_redis_connection('verify_codes')
        # 查询该号码是否注册
        have_flag = redis_conn.get('sms_{}'.format(mobile))
        if have_flag:
            return HttpResponse('该号码已注册')
        # 构建随机验证码
        sms_code = '%06d'%random.randint(0,99999)
        # 添加注册记录
        redis_conn.setex(name='sms_{}'.format(mobile), value=mobile,time=3000)
        # 添加该验证码记录
        redis_conn.setex(name='sms_code_{}'.format(mobile), value=sms_code, time=SMS_CODES_TIMES)

        # 云通讯发短信
        ccp = CCP()
        ccp.send_template_sms(mobile,[sms_code, SMS_CODES_TIMES],SMS_CODE_TEMP_ID)
        return HttpResponse(sms_code)
