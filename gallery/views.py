# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from flask import abort, send_file

from flamaster.core import http
from flamaster.gallery.models import Image

from .utils import Thumbnail

def thumbnail(img_id, geometry):
    image = Image.get(img_id) or abort(http.NOT_FOUND)
    thumbnail = Thumbnail(img_id, image, geometry, '')
    return send_file(thumbnail.thumbnail)
