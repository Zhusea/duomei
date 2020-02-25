from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView,GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from django_redis import get_redis_connection
from rest_framework_jwt.views import ObtainJSONWebToken

from .models import User
from .serializers import UserSerializer
from .serializers import UserDetailSerializer
from .serializers import UserEmailSerializer
from .serializers import AddressesSerializer
from . import constants
from .serializers import AddressTitleSerializer
from goods.models import SKU
from goods.serializers import SKUSerializer
from cart.utils import merge_cart_cookie_to_redis
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
    pagination_class = None
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

class UserGoodsHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        """添加历史纪录"""
        # 获取用户id
        user_id = request.user.id
        sku_id = request.data.get('sku_id')
        try:
            sku_obj = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return Response({'message':'没有该商品'},status=status.HTTP_400_BAD_REQUEST)
        redis_conn = get_redis_connection('history')
        pl = redis_conn.pipeline()
        # 移除已经存在的本商品浏览记录
        pl.lrem("history_%s" % user_id, 0, sku_id)
        # 添加新的浏览记录
        pl.lpush("history_%s" % user_id, sku_id)
        # 只保存最多5条记录
        pl.ltrim("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)

        pl.execute()
        return Response({'message':'ok'})

    def get(self, request):
        """获取历史记录"""

        user_id = request.user.id

        redis_conn = get_redis_connection('history')
        sku_id_list = redis_conn.lrange('history_{}'.format(user_id),0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT)

        sku_obj = []
        for sku_id in sku_id_list:
            try:
                sku = SKU.objects.get(id=sku_id)
            except SKU.DoesNotExist:
                pass
            else:
                sku_obj.append(sku)

        serializer = SKUSerializer(sku_obj, many=True)

        return Response(serializer.data)


class UserAuthorizeView(ObtainJSONWebToken):
    def post(self, request):
        response = super().post(request)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            response = merge_cart_cookie_to_redis(request, response, user)

        return response
