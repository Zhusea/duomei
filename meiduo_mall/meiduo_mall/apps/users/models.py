from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as JWTSerializer
from django.conf import settings
from itsdangerous import BadData

from meiduo_mall.utils.models import BaseModel
# Create your models here.

class User(AbstractUser):
    """用户模型类"""

    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_activate = models.BooleanField(default=False,verbose_name='邮件验证状态')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name




    def get_email_url(self, secret_key=None, expires=None):
        """
             对openid进行加密:
             openid: QQ授权用户的openid
             secret_key: 密钥
             expires: token有效时间
             """
        if secret_key is None:
            secret_key = settings.SECRET_KEY

        if expires is None:
            expires = settings.EXPIRES_IN

        serializer = JWTSerializer(secret_key, expires)

        token = serializer.dumps({'user_id': self.id,'email':self.email}).decode()
        url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return url


    @classmethod
    def check_verify_email_token(cls,token):
        serializer = JWTSerializer(settings.SECRET_KEY, settings.EXPIRES_IN)

        try:
            data = serializer.loads(token)
        except BadData :
            return False
        else:
            print(data['user_id'])
            User.objects.filter(email=data['email'], id=data['user_id']).update(email_activate=True)
            return True



# 设置默认地址
class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
    # is_default = models.BooleanField(default=False, verbose_name='是否默认')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']