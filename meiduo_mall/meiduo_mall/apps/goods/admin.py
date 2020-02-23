from django.contrib import admin

from . import models
class SKUAdmin(admin.ModelAdmin):
    """商品Admin管理类"""
    def save_model(self, request, obj, form, change):
        # 进行数据保存
        obj.save()

        # 附加操作: 发送重新生成指定商品详情页面任务
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)


class SKUSpecificationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()

        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()

        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


class SKUImageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()

        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

        # 设置SKU默认图片
        sku = obj.sku
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url
            sku.save()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()

        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)



class GoodsCategoryAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()

        from celery_tasks.html.tasks import generate_static_list_html
        generate_static_list_html.delay()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()

        from celery_tasks.html.tasks import generate_static_list_html
        generate_static_list_html.delay()


class GoodsChannelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()

        from celery_tasks.html.tasks import generate_static_list_html
        generate_static_list_html.delay()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()

        from celery_tasks.html.tasks import generate_static_list_html
        generate_static_list_html.delay()


admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel, GoodsChannelAdmin)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
admin.site.register(models.SKUImage, SKUImageAdmin)