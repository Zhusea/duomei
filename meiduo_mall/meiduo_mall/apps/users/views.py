from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView,GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action

from .models import User
from .serializers import UserSerializer
from .serializers import UserDetailSerializer
from .serializers import UserEmailSerializer
from .serializers import AddressesSerializer
from . import constants
from .serializers import AddressTitleSerializer
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



class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = AddressesSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.filter(is_deleted=False).count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)