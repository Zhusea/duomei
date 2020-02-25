from rest_framework import serializers
from rest_framework.response import Response

from goods.models import SKU

class CartSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='sku_id',min_value=1,required=True)
    count = serializers.IntegerField(label='数量',min_value=1, required=True)
    chioce = serializers.BooleanField(label='是否选择',default=True)



    def validate(self, attrs):
        sku_id = attrs['sku_id']
        count = attrs['count']
        try:
            sku = SKU.objects.get(id=sku_id)
            real_count = sku.stock
        except SKU.DoesNotExist:
            raise serializers.ValidationError('没有该商品')


        if real_count<count:
            raise serializers.ValidationError('库存不够')


        return attrs

class GetCartSerializer(serializers.ModelSerializer):

    count = serializers.IntegerField(label='购买数量',required=True, min_value=1)
    chioce = serializers.BooleanField(label='是否勾选',required=True)

    class Meta:
        model = SKU
        fields = ['count', 'chioce', 'id', 'name', 'default_image_url','price']




class DeleteCartSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='商品id',min_value=1)


    def validate(self, attrs):
        sku_id = attrs['sku_id']
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('该商品不存在')

        return attrs