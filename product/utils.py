from flask import current_app
from werkzeug.local import LocalProxy
from werkzeug.utils import import_string


def import_shop_object(key):
    shop = current_app.config['SHOP_ID']
    shop_settings = current_app.config['SHOPS'][shop]
    return import_string(shop_settings[key])


def get_order_class():
    key = 'order'
    return LocalProxy(import_shop_object(key))


def get_cart_class():
    key = 'cart'
    return LocalProxy(import_shop_object(key))
