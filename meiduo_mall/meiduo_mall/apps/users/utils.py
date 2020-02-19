"""user应用的公共方法"""
from django.contrib.auth.backends import ModelBackend
import re

from .models import User


def jwt_response_payload_handler(token, user, request):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }



def user_by_account(account):
    """
    根据account来查询suer对象
    :param account: usernamem or mobile
    :return: user_obj or None
    """

    try:
        # 判断account是username还是 mobile
        if re.match(r'1[3-9]\d{9}',account):
            # account是mobile
            user_obj = User.objects.get(mobile=account)
        else:
            # account是username
            user_obj = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user_obj


class UsernameMobileAuthBackend(ModelBackend):
    """实现用户名和电话号码登陆"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        :param request:
        :param username:  传递可能是用户名或者是电话号码
        :param password:   用户密码
        :param kwargs:
        :return:  登陆校验成功返回一个user对象，失败则返回None
        """

        # 1、根据username来获取user对象
        user_obj = user_by_account(username)
        # 2、判断该对象是否存在，存在就进行密码校验,校验成功则返回user_obj 不成功则返回None
        if user_obj is not None and user_obj.check_password(password):
            return user_obj
