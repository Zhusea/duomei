from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django_redis import get_redis_connection

from .utils import OAuthQQ
from users.models import User
from .models import OAuthQQUser

class OAuthQQUserSerializer(ModelSerializer):
    """QQ登陆序列化器"""
    sms_code = serializers.CharField(label='短信验证码',write_only=True)
    token = serializers.CharField(label='JWT_token', read_only=True)
    access_token = serializers.CharField(label='access_token', write_only=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$', write_only=True)

    class Meta:
        model = User
        fields = ('id', 'mobile', 'password', 'sms_code', 'access_token', 'username', 'token')

        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            },
            'username': {
                'read_only': True
            }
        }


    def validate(self, attrs):
        sms_code = attrs['sms_code']
        mobile = attrs['mobile']

        # 1、校验短信验证码
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_code_{}'.format(mobile))
        # 1.1校验短信验证码是否失效
        if real_sms_code is None:
            raise serializers.ValidationError('短信验证码失效')
        # 1.2、校验短信验证码是否正确
        if sms_code != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        # 2、根据mobile来查看该用户是否注册
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 2.1、没有注册
            user = None
        else:
            # 2.2、注册过，则校验该密码是否正确
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')
        # 2.3、添加user属性
        attrs['user'] = user

        # 3、校验access_token 是否正确,返回值是openid
        access_token = attrs['access_token']
        openid = OAuthQQ.check_access_token(access_token)
        # 3.1 判断openid是否有效
        if openid is None:
            #3.1.1 无效
            raise serializers.ValidationError('access_token无效')
        # 3.1.2 有效,添加openid属性
        attrs['openid'] = openid

        return attrs


    def create(self, validated_data):
        """
                  1、判断该用户是否注册
                      1.1 注册，则将该openid与user进行绑定
                      1.2 没有注册，则注册一个user然后将openid进行绑定
                  :param self:
                  :param validated_data: 校验过后的数据，有user，mobile，password，openid
                  :return: user对象
                  """
        user = validated_data['user']

        if user is None:
            # 没有注册，创建user
            password = validated_data['password']
            mobile = validated_data['mobile']
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)

        # 绑定openid
        openid = validated_data['openid']
        OAuthQQUser.objects.create(openid=openid, user=user)

        # 签发jwt token
        # 由服务器签发一个jwt token，保存用户身份信息
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 生成载荷信息(payload)
        payload = jwt_payload_handler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)

        # 给user对象增加一个属性token，保存jwt token信息
        user.token = token

        return user


