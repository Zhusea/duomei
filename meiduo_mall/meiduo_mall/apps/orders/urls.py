from django.conf.urls import url

from . import views
urlpatterns = [
    url(r'^order/settlement/$',views.SetOrderView.as_view()),  # 提交订单
    url(r'^orders/$',views.CreateOrderView.as_view()),  # 订单的创建
    url(r'^orders/(?P<order_id>\d+)/payment/$', views.OrderPayView.as_view()),  # 订单支付
    url(r'^payment/status/$',views.PaymentStatusView.as_view()),  # 订单支付状态校验

]
