from __future__ import absolute_import
from flask import current_app

from flamaster.core.decorators import api_resource
from flamaster.core.resources import ModelResource
from flamaster.core.utils import null_fields_filter, jsonify_status_code
from flamaster.core import http
from flask.ext.security import roles_required
from flask import request


from . import bp
from .models import FlatPage

import trafaret as t


@api_resource(bp, 'pages', {'id': None})
class FlatPageResource(ModelResource):

    validation = t.Dict({
        'shop_id': t.String,
        'name': t.String,
        'slug': t.String,
        t.Key('registration_required', default=False): t.Bool,
        'template_name': t.String,
        'content': t.String
    }).make_optional('shop_id', 'template_name').ignore_extra('*')

    filters_map = t.Dict({
        t.Key('shop_id', default=current_app.config['SHOP_ID']): t.String
    }).make_optional('*').ignore_extra('*')

    model = FlatPage
    method_decorators = {'post': roles_required('admin'),
                         'put': roles_required('admin'),
                         'delete': roles_required('admin')}

    def put(self, id):
        status = http.ACCEPTED
        data = request.json or abort(http.BAD_REQUEST)

        try:
            data = self.clean(data)
            data = null_fields_filter(['template_name', 'shop_id'], data)
        except t.DataError as e:
            return jsonify_status_code(e.as_dict(), http.BAD_REQUEST)

        instance = self.get_object(id).update(with_reload=True, **data)
        response = self.serialize(instance)
        return jsonify_status_code(response, status)
