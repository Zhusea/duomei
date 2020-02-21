"""
使用FastDFS和nginx的好处：
1.提高存储容量方便扩展
2.提高提供照片的效率
3.文件内容不重复
"""

from fdfs_client.client import Fdfs_client  # 导入FastDFS的客服端类
from django.core.files.storage import Storage  # 导入django后台上传文件的类
from django.utils.deconstruct import deconstructible
from django.conf import settings

"""使用自定义的模块需要在配置作相关配置,好在Django在使用的时候，使用我们自己写的模块"""
@deconstructible
class FastDFSStorage(Storage):
    """fdfs储存文件"""
    def __init__(self, client_conf=None, base_url=None):
        '''初始化'''
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url

    def _open(self, name, more='rb'):
        """打开文件的操作"""
        pass

    def _save(self, name, content):
        '''保存文件时使用'''
        # name:你选择上传文件的名字
        # content:包含你上传文件内容的File对象

        # 创建一个Fdfs_client对象
        client = Fdfs_client(self.client_conf)

        # 上传文件到fast dfs系统中
        res = client.upload_by_buffer(content.read())

        # dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到fast dfs失败')

        # 获取返回的文件ID
        filename = res.get('Remote file_id')

        return filename

    def url(self, name):
        urls =self.base_url+name  # 返回获取该文件的链接
        return urls

    def exists(self, name):
        """判断该文件名是否可用，可用返回False，采用的FastDFS,都可以存储，不会存在文件名相同而不能存储的情况"""
        return False