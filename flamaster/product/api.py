from flask import abort, g, request, session
from flamaster.app import app

import trafaret as t

from flamaster.core.utils import jsonify
from flamaster.core.decorators import api_resource
from flamaster.core.resource_base import BaseResource

from . import product
from .models import Product

__all__ = ['ProductResource']


@api_resource(product, 'products', {'id': None})
class ProductResource(BaseResource):

    def get(self, id=None):
        return jsonify({"qqq": Product.query.with_entities(Product.slug).all()})

    def post(self):
        return jsonify({})

    def put(self, id):
        return jsonify({})

    def delete(self, id):
        return jsonify({})
