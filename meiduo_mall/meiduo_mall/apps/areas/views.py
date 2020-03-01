from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .serializers import AreaSerializer
from .serializers import AreaSubsSerlializer
from .models import Area
# Create your views here.


class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    pagination_class = None

    def get_queryset(self):
        """
        提供数据集
        """
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        """
        提供序列化器
        """
        if self.action == 'list':
            return AreaSerializer
        else:
            return AreaSubsSerlializer