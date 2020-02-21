from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from .views import UsernameView
from .views import MobileView
from .views import RegisterView
from .views import UserDetailView
from .views import UserEmailView
from .views import EmailVerificationView
from .views import AddressViewSet


urlpatterns = [
    url(r'^username/(?P<username>\w{5,20})/$', UsernameView.as_view()),  # 校验username路由
    url(r'^mobile/(?P<mobile>1[3456789]\d{9})/$', MobileView.as_view()),  # 校验电话号码路由
    url(r'^users/$', RegisterView.as_view()),  # 注册用户路由
    url(r'^authorizations/$', obtain_jwt_token),  # 登陆路由
    url(r'^user/$',UserDetailView.as_view()),  # 用户跟人信息详情页
    url(r'^email/$',UserEmailView.as_view()),  # 修改用户的email信息
    url(r'^emails/verification/$', EmailVerificationView.as_view()),  # 邮件校验路由
    # url(r'^addresses/$', AddresssesView.as_view()),  # 个人地址数据路由

]
router = DefaultRouter()
router.register('addresses', AddressViewSet, basename='addresses')
urlpatterns += router.urls

