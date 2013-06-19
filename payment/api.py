from flamaster.core.resources import Resource
from flamaster.core.decorators import api_resource, method_wrapper
from flamaster.core import http
from flamaster.core.utils import jsonify_status_code

from flask import current_app
from . import payment as bp


@api_resource(bp, 'settings', {'short': None})
class SettingsResource(Resource):

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def put(self, **kwargs):
        return ''

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def post(self, **kwargs):
        return ''

    @method_wrapper(http.METHOD_NOT_ALLOWED)
    def delete(self, **kwargs):
        return ''

    def get(self, **kwargs):
        settings = current_app.config['PAYMENT_METHODS']
        paymill = settings.get('paymill')

        response = {}

        if paymill:
            response.update({
                'paymill': {
                    'PUBLIC_KEY': paymill['settings'].get('PUBLIC_KEY')
                }
            })

        return jsonify_status_code(response)
