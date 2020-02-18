from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView,ListAPIView,CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer

# Create your views here.

# url username/(?P<username>\w{5,20})
class UsernameView(APIView):
    """用户名校验视图"""

    def get(self, request, username):

        username_count = User.objects.filter(username=username).count()

        return Response({'username':username, 'count':username_count})


# url mobile/(?P<mobile>1[345678]\d{9}$)
class MobileView(APIView):
    """电话号码校视图"""
    def get(self, request, mobile):

        mobile_count = User.objects.filter(mobile=mobile).count()

        return Response({'mobile':mobile, 'count':mobile_count})


# url users/
class RegisterView(CreateAPIView):
    """用户注册视图"""
    serializer_class = UserSerializer


