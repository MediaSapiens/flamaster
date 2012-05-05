from flamaster.core.utils import jsonify
from flamaster.core.decorators import api_resource
from flamaster.core.resource_base import BaseResource

from . import product
from .models import Product

__all__ = ['ProductResource']


@api_resource(product, 'products', {'id': int})
class ProductResource(BaseResource):

    def get(self, id=None):
        if id is not None:
            response = Product.query.get_or_404(id).as_dict()
        else:
            response = [product.as_dict() for product in Product.query.all()]
        return jsonify(response)
