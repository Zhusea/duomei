from django.conf.urls import url
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token


from .views import UsernameView
from .views import MobileView
from .views import RegisterView

urlpatterns = [
    url(r'^username/(?P<username>\w{5,20})$', UsernameView.as_view(), name='username'),  # 校验username路由
    url(r'^mobile/(?P<mobile>1[3456789]\d{9})$', MobileView.as_view(), name='mobile'),  # 校验电话号码路由
    url(r'^users/$', RegisterView.as_view(), name='users'),  # 注册用户路由
    url(r'^authorizations/$', obtain_jwt_token),  # 登陆路由
]

