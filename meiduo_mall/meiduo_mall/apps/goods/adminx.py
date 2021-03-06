# from django.contrib import admin
import xadmin
from . import models
# class SKUAdmin(object):
#     """商品Admin管理类"""
#     def save_model(self, request, obj, form, change):
#         # 进行数据保存
#         obj.save()
#
#         # 附加操作: 发送重新生成指定商品详情页面任务
#         from celery_tasks.html.tasks import generate_static_sku_detail_html
#         generate_static_sku_detail_html.delay(obj.id)

#
# class SKUSpecificationAdmin(object):
#     def save_model(self, request, obj, form, change):
#         obj.save()
#
#         from celery_tasks.html.tasks import generate_static_sku_detail_html
#         generate_static_sku_detail_html.delay(obj.sku.id)
#
#     def delete_model(self, request, obj):
#         sku_id = obj.sku.id
#         obj.delete()
#
#         from celery_tasks.html.tasks import generate_static_sku_detail_html
#         generate_static_sku_detail_html.delay(sku_id)
#
#
# class SKUImageAdmin(object):
#     def save_model(self, request, obj, form, change):
#         obj.save()
#
#         from celery_tasks.html.tasks import generate_static_sku_detail_html
#         generate_static_sku_detail_html.delay(obj.sku.id)
#
#         # 设置SKU默认图片
#         sku = obj.sku
#         if not sku.default_image_url:
#             sku.default_image_url = obj.image.url
#             sku.save()
#
#     def delete_model(self, request, obj):
#         sku_id = obj.sku.id
#         obj.delete()
#
#         from celery_tasks.html.tasks import generate_static_sku_detail_html
#         generate_static_sku_detail_html.delay(sku_id)
#
#
#
# class GoodsCategoryAdmin(object):
#     def save_model(self, request, obj, form, change):
#         obj.save()
#
#         from celery_tasks.html.tasks import generate_static_list_html
#         generate_static_list_html.delay()
#
#     def delete_model(self, request, obj):
#         sku_id = obj.sku.id
#         obj.delete()
#
#         from celery_tasks.html.tasks import generate_static_list_html
#         generate_static_list_html.delay()
#
#
# class GoodsChannelAdmin(object):
#     def save_model(self, request, obj, form, change):
#         obj.save()
#
#         from celery_tasks.html.tasks import generate_static_list_html,generate_static_search_html
#         generate_static_list_html.delay()
#         generate_static_list_html.delay()
#
#     def delete_model(self, request, obj):
#         sku_id = obj.sku.id
#         obj.delete()
#
#         from celery_tasks.html.tasks import generate_static_list_html,generate_static_search_html
#         generate_static_list_html.delay()
#         generate_static_search_html.delay()


xadmin.site.register(models.GoodsCategory)
xadmin.site.register(models.GoodsChannel)
xadmin.site.register(models.Goods)
xadmin.site.register(models.Brand)
xadmin.site.register(models.GoodsSpecification)
xadmin.site.register(models.SpecificationOption)
xadmin.site.register(models.SKU)
xadmin.site.register(models.SKUSpecification)
xadmin.site.register(models.SKUImage)