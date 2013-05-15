from functools import partial
from flask import Blueprint
from flamaster.core.utils import add_api_rule, add_url_rule

bp = Blueprint('gallery', __name__, url_prefix='/gallery')
add_url = partial(add_url_rule, bp, 'flamaster.gallery.views')


def add_resource(endpoint, pk_def, import_name):
    return add_api_rule(bp, endpoint, pk_def, import_name)

add_resource('images', {'id': None}, 'flamaster.gallery.api.ImageResource')
add_url('/<img_id>/<geometry>', 'thumbnail')
