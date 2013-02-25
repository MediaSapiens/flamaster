from flask import Blueprint

core = Blueprint('core', __name__, url_prefix='', template_folder='templates')


import api
import views

from .countries import COUNTRY_CHOICES
from .columns import ChoiceType
from .commands import CreateAll, DropAll
from .decorators import api_resource
from .utils import lazy_cascade, plural_underscored
# import template_ext
