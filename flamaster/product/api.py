from flask import abort, g, request
from flamaster.app import app
import trafaret as t

from flamaster.core.utils import jsonify
from flamaster.core.decorators import api_resource
from flamaster.core.resource_base import BaseResource

from . import product
from .models import Product

__all__ = ['ProductResource']


@api_resource(product, 'products', {'id': int})
class ProductResource(BaseResource):

    def get(self, id=None):
        uid = _creater()
        if id is None:
            products = Product.query.filter_by(created_by=uid)
            response = [(one_pro.slug, one_pro.as_dict())\
                        for one_pro in products]
            response = dict(response)
        else:
            product = Product.query.filter_by(
                id=id, created_by=uid).first_or_404()
            response = product.as_dict()
        return jsonify(response)

    def post(self):
        uid = _creater()
        data = request.json or abort(400)
        data.update({'created_by': uid})
        try:
            product = Product.create(**data)
            data, status = product.as_dict(), 201
        except t.DataError as e:
            data, status = e.as_dict(), 400

        return jsonify(data, status=status)

    def put(self, id):
        uid = _creater()
        data = request.json or abort(400)
        data.update({'created_by': uid})
        try:
            product = Product.query.get_or_404(id)
            product.update(**data)
            data, status = product.as_dict(), 201
        except t.DataError as e:
            data, status = e.as_dict(), 400
        return jsonify(data, status=status)

    def delete(self, id):
        uid = _creater()
        try:
            Product.query.filter_by(id=id, created_by=uid).delete()
            data, status = {}, 200
        except t.DataError as e:
            data, status = e.as_dict(), 400

        return jsonify(data, status=status)


def _creater():
    if g.user.role == app.config['ADMIN_ROLE']:
        uid = request.json.get('user_id', False) or g.user.id
    else:
        uid = g.user.id or abort(401)
    return uid
