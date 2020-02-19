from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token


from .views import UsernameView
from .views import MobileView
from .views import RegisterView
from .views import UserDetailView
from .views import UserEmailView
from .views import EmailVerificationView


urlpatterns = [
    url(r'^username/(?P<username>\w{5,20})/$', UsernameView.as_view()),  # 校验username路由
    url(r'^mobile/(?P<mobile>1[3456789]\d{9})/$', MobileView.as_view()),  # 校验电话号码路由
    url(r'^users/$', RegisterView.as_view()),  # 注册用户路由
    url(r'^authorizations/$', obtain_jwt_token),  # 登陆路由
    url(r'^user/$',UserDetailView.as_view()),  # 用户跟人信息详情页
    url(r'^email/$',UserEmailView.as_view()),  # 修改用户的email信息
    url(r'^emails/verification/$', EmailVerificationView.as_view()),  # 邮件校验路由

]

