from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import AreasViewSet

router = DefaultRouter()

router.register(r'areas', AreasViewSet, basename='areas')

urlpatterns = [

]

urlpatterns += router.urls