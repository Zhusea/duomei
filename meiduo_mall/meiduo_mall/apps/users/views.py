from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView,CreateAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import User
from .serializers import UserSerializer
from .serializers import UserDetailSerializer
from .serializers import UserEmailSerializer
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

# url user/
class UserDetailView(RetrieveAPIView):
    """用户详情页"""
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):

        return self.request.user

# url email/
class UserEmailView(UpdateAPIView):
    serializer_class = UserEmailSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

# url emails/verification/
class EmailVerificationView(APIView):

    def get(self, request):

        token = request.query_params.get('token')
        if not token:
            return Response({'message':'缺少token'},status=status.HTTP_400_BAD_REQUEST)


        ret = User.check_verify_email_token(token)

        if not ret:
            return Response({'message':'token错误'},status=status.HTTP_400_BAD_REQUEST)

        return Response({'message':'OK'})

