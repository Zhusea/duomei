from rest_framework import serializers
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings
import re

from .models import User
from celery_tasks.email.tasks import send_email

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器类"""
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='身份认证',read_only=True)

    class Meta:
        model = User
        fields = ['id','username','token','mobile', 'password', 'password2', 'sms_code', 'allow']
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            },
            'id':{
                'read_only':True,
            }
        }

    def validate_username(self,value):
        """校验用户名是否重复"""
        username_count = User.objects.filter(username=value).count()
        if username_count > 0:
            raise serializers.ValidationError('该用户名已注册')
        return value

    def validate_mobile(self, value):
        """校验电话号码"""
        mobile_count = User.objects.filter(mobile=value).count()
        if mobile_count > 0:
            raise serializers.ValidationError('该号码已注册')

        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('电话号码格式不对')
        return value

    def validate_allow(self, value):
        """校验是否同意用户协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):
        """1、校验两次密码是否一致
        2、校验验证码"""
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')
        #redis获取验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        sms_code = redis_conn.get('sms_code_{}'.format(mobile))
        # 该验证码不存在，说明该验证码时效已过
        if sms_code is None:
            raise serializers.ValidationError('验证码失效')
        # 验证码不匹配
        if sms_code.decode() != data['sms_code']:
            raise serializers.ValidationError('验证码不一致')
        return data

    def create(self, validated_data):
        """创建用户"""
        # 删除创建用户不需要的字段
        del validated_data['password2']
        del validated_data['allow']
        del validated_data['sms_code']

        # 使用父类的create方法创建user对象
        # user = super().create(validated_data)
        # user.save()

        # 使用orm提供的创建user对象
        user = User.objects.create_user(**validated_data)  # 注册成功该用户就是激活状态

        # 补充生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 生成载荷信息(payload)
        payload = jwt_payload_handler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)
        # 给user对象增加一个属性token，保存jwt token信息
        user.token = token

        return user



class UserDetailSerializer(serializers.ModelSerializer):
    """用户个人信息序列化器"""
    class Meta:
        model = User
        fields = ['id','username','email', 'email_activate','mobile']



class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        """

        :param instance: user对象
        :param validated_data:  被校验的数据
        :return:
        """
        email = validated_data['email']
        instance.email = email
        instance.save()
        # 发送邮件
        url = instance.get_email_url()
        send_email.delay(email, url)

        return instance

