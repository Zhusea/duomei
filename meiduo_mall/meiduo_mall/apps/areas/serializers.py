from rest_framework import serializers

from .models import Area


class AreaSerializer(serializers.ModelSerializer):
    """最高级地区序列化器"""
    class Meta:
        model = Area
        fields = ['id', 'name']


class AreaSubsSerlializer(serializers.ModelSerializer):
    """子集地区序列化器"""
    subs = AreaSerializer(many=True, read_only=True)
    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']
