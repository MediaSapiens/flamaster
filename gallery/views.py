# -*- encoding: utf-8 -*-
from flask import abort, send_file

from flamaster.core import http
from flamaster.gallery.models import Image

from . import bp
from .utils import get_thumbnail


@bp.route('/<img_id>/<geometry>')
def thumbnail(img_id, geometry):
    image = Image.get(img_id) or abort(http.NOT_FOUND)
    file_object = get_thumbnail(img_id, image, geometry, '')
    return send_file(open(file_object, 'r'))
