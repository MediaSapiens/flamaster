import trafaret as t
from flask.ext.security import roles_required

from flamaster.core.decorators import api_resource
from flamaster.core.resources import ModelResource

from . import flatpages
from .models import FlatPage

__all__ = ['FlatPageResource']


@api_resource(flatpages, 'pages', {'id': None})
class FlatPageResource(ModelResource):

    validation = t.Dict({'name': t.String,
                         'content': t.String}).ignore_extra('*')
    model = FlatPage
    method_decorators = {'post': roles_required('admin'),
                         'put': roles_required('admin')}
