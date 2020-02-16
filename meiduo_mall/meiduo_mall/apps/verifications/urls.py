from django.conf.urls import url
from .views import SMSCodesView
from rest_framework import routers

# from verifications import views
urlpatterns = [
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})$', SMSCodesView.as_view()),
]

