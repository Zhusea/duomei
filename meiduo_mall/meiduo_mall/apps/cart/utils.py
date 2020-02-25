from django_redis import get_redis_connection
import pickle
import base64

def merge_cart_cookie_to_redis(request, response, user):
    """
    合并cookies和redis中的购物车数据
    :param request:
    :param response:
    :param user:
    :return:  返回response
    """
    cookie_cart = request.COOKIES.get('cart')

    if not cookie_cart:
        return response
    # 获取cookies中的购物车数据
    cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart))

    redis_conn = get_redis_connection('cart')
    # 获取redis中数据库的数据
    redis_dict = redis_conn.hgetall('cart_{}'.format(user.id))

    # cart为全部的购物车数据
    cart = {}
    # 勾选的sku_id
    chioce_sku_id = []
    # 将redis中的字典存储为bytes 全部改为int类型
    for sku_id,count in redis_dict.items():
        cart[int(sku_id)] = int(count)

    # 将cookie中的购物车数据加入cart中
    for sku_id, count_chioce_dict in cookie_cart_dict.items():
        cart[sku_id] = count_chioce_dict['count']

        # 将勾选的sku_id 加入列表中
        if count_chioce_dict['chioce']:
            chioce_sku_id.append(sku_id)


    pl = redis_conn.pipeline()
    if cart:
        pl.hmset('cart_{}'.format(user.id), cart)

        pl.sadd('cart_chioce_{}'.format(user.id), *chioce_sku_id)

    pl.execute()
    response.delete_cookie('cart')
    return response