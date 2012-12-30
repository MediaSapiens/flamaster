# encoding: utf-8

from flask import abort, g

from flamaster.core import http
from flamaster.gallery.models import Image

from . import thumbnail, cache
from .utils import get_thumbnail


@cache.memoize(60)
def check_thumbnail(uid, img_id, geometry_string, options_string):
    image = Image.query.get_or_404(img_id)
    image.access(uid) or abort(http.FORBIDDEN)
    return get_thumbnail(image.fullpath, geometry_string, options_string)


@thumbnail.route('/<img_id>/<geometry>/<options>', methods=['GET'])
def thumbnail(img_id, geometry, options=None):
    user_id = not g.user.is_anonymous() and g.user.id
    return str(check_thumbnail(user_id, img_id, geometry, options))
