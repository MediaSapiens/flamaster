from flask import session, current_app
from flask.ext.babel import get_locale

from . import core, http
from .decorators import api_resource
from .resources import Resource
from .utils import jsonify_status_code


@api_resource(core, 'locale', {'short': None})
class LocaleResource(Resource):

    def get(self, short=None):
        locale = get_locale()
        objects = []
        for short, name in current_app.config['LANGUAGES'].items():
            objects.append({
                'name': name,
                'short': short,
                'is_set': locale.language == short
            })

        return jsonify_status_code({'objects': objects})

    def put(self, short=None):
        session[current_app.config['LOCALE_KEY']] = short
        locale_obj = {
            'short': short,
            'is_set': True,
            'name': current_app.config['LANGUAGES'][short]
        }
        return jsonify_status_code(locale_obj, http.ACCEPTED)
