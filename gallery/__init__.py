from flask import Blueprint
from flamaster.core.utils import LazyView, add_api_rule

bp = Blueprint('gallery', __name__, url_prefix='/gallery')

add_url = lambda path, view: bp.add_url_rule(path, view_func=LazyView(view))


def add_resource(endpoint, pk_def, import_name):
    return add_api_rule(bp, endpoint, pk_def, import_name)

add_resource('images', {'id': None}, 'flamaster.gallery.api.ImageResource')
add_url('/<img_id>/<geometry>', 'flamaster.gallery.views.thumbnail')
