# -*- encoding: utf-8 -*-
from __future__ import absolute_import

from flask import abort, redirect, send_file

from flamaster.core import http
from flamaster.core.utils import x_accel_gridfs
from flamaster.core.documents import FileModel

import settings
from .utils import Thumbnail


def thumbnail(img_id, geometry):
    image = FileModel.get(img_id) or abort(http.NOT_FOUND)
    thumbnail = Thumbnail(img_id, image, geometry, '').thumbnail
    path = thumbnail.path

    if settings.USE_S3:
        return redirect(path)
    else:
        return send_file(path)
