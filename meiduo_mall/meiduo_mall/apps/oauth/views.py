from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from .utils import OAuthQQ
from rest_framework.response import Response
from rest_framework import status
import logging
from rest_framework_jwt.settings import api_settings

from .exceptions import QQAPIError
from .models import OAuthQQUser
from .serializers import OAuthQQUserSerializer
# Create your views here.
# 获取logger

logger = logging.getLogger('django')

#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
class QQAuthURLView(APIView):
    """QQ的登陆视图"""

    def get(self, request):
        """
        :param request:
        :return: 返回一个url给前端
        """
        next = request.query_params.get('next', '/')
        oauth = OAuthQQ(state=next)
        url = oauth.get_login_url()

        return Response({'login_url':url},status=status.HTTP_200_OK)



class QQAuthUserView(CreateAPIView):
    """
    1、获取code
    2、获取accesstoke
    """
    serializer_class = OAuthQQUserSerializer
    def get(self, request):
        # 1、从request中提取获取code参数
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        # 2、由code向qq服务器发起请求获取Access Token 参数
        oauth = OAuthQQ()
        try:
            access_token = oauth.get_access_token(code=code)
            # print(access_token)
        # 3、根据QQ服务器传递的Access Token 再次向QQ服务器发起请求获取openid
            openid = oauth.get_openid(access_token=access_token)
            # print(openid)
        except QQAPIError as e:
            logger.error(e)
            return Response({'message': 'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 4、在根据openid来确定自己的user中是否绑定该openid
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 4.2 该openid第一次登陆，则返回自己根据opemid生成的access_token给前端
            token = OAuthQQ.generate_save_user_token(openid)
            return Response({'access_token':token})

        else:
            # 4.1该openid已注册，给前端返回jwt_token
            user = qq_user.user
            # 补充生成记录登录状态的token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            # 生成载荷信息(payload)
            payload = jwt_payload_handler(user)
            # 生成jwt token
            token = jwt_encode_handler(payload)
            # 给user对象增加一个属性token，保存jwt token信息
            user.token = token
            return Response({
                'usrename':user.username,
                'user_id':user.id,
                'token':user.token
            })