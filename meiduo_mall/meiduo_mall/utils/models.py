from django.db import models


class BaseModel(models.Model):
    update_time = models.DateField(auto_now_add=True, verbose_name='创建时间')
    create_time = models.DateField(auto_now=True, verbose_name='更新时间')
    class Meta:
        abstract = True  # 抽象模型类，不再数据库迁移生成表