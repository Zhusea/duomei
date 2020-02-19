from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as JWTSerializer
from django.conf import settings
from itsdangerous import BadData
# Create your models here.

class User(AbstractUser):
    """用户模型类"""

    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_activate = models.BooleanField(default=False,verbose_name='邮件验证状态')

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