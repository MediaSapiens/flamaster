from flask import Blueprint, current_app
from werkzeug.local import LocalProxy

core = Blueprint('core', __name__, url_prefix='', template_folder='templates')

cache = LocalProxy(lambda: current_app.extensions['cache'].cache)
db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)
mail = LocalProxy(lambda: current_app.extensions['mail'])
mongo = LocalProxy(lambda: current_app.extensions['mongoset'])

_security = LocalProxy(lambda: current_app.extensions['security'])
_social = LocalProxy(lambda: current_app.extensions['social'])


import api
import views

from .countries import COUNTRY_CHOICES
from .columns import ChoiceType
from .commands import CreateAll, DropAll
from .decorators import api_resource
from .utils import lazy_cascade, plural_underscored
# import template_ext
