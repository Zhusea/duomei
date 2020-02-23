from rest_framework.serializers import ModelSerializer

from .models import SKU
from .models import GoodsCategory,GoodsChannel

class SKUSerializer(ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id','name','price','default_image_url','comments']


class CategorySerializer(ModelSerializer):
    """
    类别序列化器
    """
    class Meta:
        model = GoodsCategory
        fields = ('id', 'name')

class ChannelSerializer(ModelSerializer):
    """
    频道序列化器
    """
    category = CategorySerializer()

    class Meta:
        model = GoodsChannel
        fields = ('category', 'url')