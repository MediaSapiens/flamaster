from flask import Blueprint, current_app
from werkzeug.local import LocalProxy

app = LocalProxy(lambda: current_app)
core = Blueprint('core', __name__, url_prefix='', template_folder='templates')
db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)
indexer = LocalProxy(lambda: current_app.extensions['indexer'])

import api
import views

from .countries import COUNTRY_CHOICES
from .columns import ChoiceType
from .commands import CreateAll, DropAll
from .decorators import api_resource
from .utils import lazy_cascade, plural_underscored
# import template_ext
