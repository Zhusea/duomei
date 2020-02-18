from django.conf import settings
from urllib.parse import urlencode,parse_qs
from urllib import request
import requests
import re
import json
from itsdangerous import TimedJSONWebSignatureSerializer as JWTSerializer
from itsdangerous import BadData

from .exceptions import QQAPIError
class OAuthQQ(object):
    """请求QQ服务器类"""
    SECRET_KEY = settings.QQ_CLIENT_SECRET
    EXPIRES_IN = 600

    def __init__(self, client_secret=None, client_id=None, redirect_uri=None,state=None):
        # QQ网站应用客户端id
        self.client_id = client_id or settings.QQ_CLIENT_ID
        # 网站回调url网址
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        # next地址
        self.state = state or settings.QQ_STATE
        # QQ网站应用客户端安全密钥
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET

    def get_login_url(self):
        """
        构建QQ的登陆的code参数网址:
        """
        # 组织参数
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info'
        }

        # 拼接url地址
        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)

        return url

    def get_access_token(self, code):
        """
        根据code获取QQ服务器法返回的access_token
        :param code:
        :return: access_token
        """
        # 组织参数
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret':self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code,
        }

        # 拼接url地址
        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)
        try:
            response = requests.get(url=url)
        except Exception as e:
            raise QQAPIError(str(e))
        response = response.content.decode()
        try:
            access_token = re.findall(r'(?<=access_token=).*?(?=&)', response)[0]
        except Exception as e:
            return QQAPIError(str(response))
        else:
            return access_token

    def get_openid(self, access_token):
        """
        根据access_token来获取openid
        :param access_token:
        :return: openid
        """
        # 组织参数
        params = {
            'access_token': access_token,
        }

        # 拼接url地址
        url = 'https://graph.qq.com/oauth2.0/me?' + urlencode(params)
        try:
            response = request.urlopen(url=url)
        except Exception as e:
            raise QQAPIError(str(e))
        response = response.read().decode()
        try:
            openid = re.findall(r'(?<="openid":").*?(?="} )', response)[0]
        except Exception as e:

            raise QQAPIError(str(response))
        else:
            # 获取openid
            return openid

    @classmethod
    def generate_save_user_token(cls, openid, secret_key=None, expires=None):
        """
        对openid进行加密:
        openid: QQ授权用户的openid
        secret_key: 密钥
        expires: token有效时间
        """
        if secret_key is None:
            secret_key = cls.SECRET_KEY

        if expires is None:
            expires = cls.EXPIRES_IN

        serializer = JWTSerializer(secret_key, expires)

        token = serializer.dumps({'openid': openid})
        return token.decode()
    @classmethod
    def check_access_token(cls, access_token, secret_key=None, expires=None):
        """
        校验access_token是否正确，对access_token解密，获取对应的openid:
        access_token: 自己生成的access_token
        secret_key: 密钥
        expires: token有效时间
        """
        if secret_key is None:
            secret_key = cls.SECRET_KEY

        if expires is None:
            expires = cls.EXPIRES_IN

        serializer = JWTSerializer(secret_key=secret_key,expires_in=expires)
        try:
            data = serializer.loads(access_token)
        except BadData :
            return None
        else:
            return data.get('openid')