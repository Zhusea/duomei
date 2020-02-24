from django.template import loader
import os
from django.conf import settings

from celery_tasks.main import app
from contents.utils import get_categories
from goods.models import SKU

@app.task(name='generate_static_sku_detail_html')
def generate_static_sku_detail_html(sku_id):

    categories = get_categories()

    sku = SKU.objects.get(id=sku_id)
    sku.images = sku.skuimage_set.all()   # sku的图片信息


    goods = sku.goods  # 该sku对应的spu
    goods.channel = goods.category1.goodschannel_set.all()[0]  # spu对应的频道信息


    sku_specs = sku.skuspecification_set.order_by('spec_id')  # 该商品的具体规格

    sku_key = []  # 该商品的规格值的id
    for spec in sku_specs:
        sku_key.append(spec.option.id)


    # 获取当前商品的所有SKU
    skus = goods.sku_set.all()

    # 构建不同规格参数（选项）的sku字典
    # spec_sku_map = {
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     ...
    # }
    spec_sku_map = {}
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.skuspecification_set.order_by('spec_id')
        # 用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    specs = goods.goodsspecification_set.order_by('id')
    # 若当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(specs):
        return
    for index, spec in enumerate(specs):
        # 复制当前sku的规格键
        key = sku_key[:]
        # 该规格的选项
        options = spec.specificationoption_set.all()
        for option in options:
            # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))

        spec.options = options

    # 使用`detail.html`文件，进行模板渲染，获取渲染之后的内容
    context = {
        'categories': categories,
        'goods': goods,
        'specs': specs,
        'sku': sku
    }

    template = loader.get_template('detail.html')
    html_text = template.render(context)

    # 将渲染之后的内容保存成一个静态文件
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'goods/' + str(sku_id) + '.html')

    with open(file_path, 'w') as f:
        f.write(html_text)


@app.task(name='generate_static_list_html')
def generate_static_list_html():

    categories = get_categories()

    # 使用`detail.html`文件，进行模板渲染，获取渲染之后的内容
    context = {
        'categories': categories,
    }
    template = loader.get_template('list.html')
    html_text = template.render(context)
    # 将渲染之后的内容保存成一个静态文件
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'list.html')

    with open(file_path, 'w') as f:
        f.write(html_text)

@app.task(name='generate_static_search_html')
def generate_static_search_html():

    categories = get_categories()

    # 使用`detail.html`文件，进行模板渲染，获取渲染之后的内容
    context = {
        'categories': categories,
    }
    template = loader.get_template('search.html')
    html_text = template.render(context)
    # 将渲染之后的内容保存成一个静态文件
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'search.html')

    with open(file_path, 'w') as f:
        f.write(html_text)