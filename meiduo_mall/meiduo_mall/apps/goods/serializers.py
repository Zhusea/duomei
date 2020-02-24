from rest_framework.serializers import ModelSerializer
from drf_haystack.serializers import HaystackSerializer

from .models import SKU
from .models import GoodsCategory,GoodsChannel
from .search_indexes import SKUIndex

class SKUSerializer(ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id','name','price','default_image_url','comments']

class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')

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