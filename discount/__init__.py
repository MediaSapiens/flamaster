from flask import Blueprint

USER_CHOICE = 'user'
PRODUCT_CHOICE ='product'
CATEGORY_CHOICE ='category'
BASKET_CHOICE = 'basket'

PERCENT_CHOICE = 'percent'
CURRENCY_CHOICE = 'currency'

discount = Blueprint('discount', __name__, url_prefix='/discount')


import api
# import views