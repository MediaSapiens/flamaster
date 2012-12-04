from flask import session, current_app

from . import core, http
from .decorators import api_resource
from .resources import Resource
from .utils import jsonify_status_code

LOCALE_KEY = 'locale'


@api_resource(core, 'locale', {'short': None})
class LocaleResource(Resource):

    def get(self, short=None):
        locale = session.get(LOCALE_KEY,
                             current_app.config['BABEL_DEFAULT_LOCALE'])
        objects = []
        for short, name in current_app.config['LANGUAES'].items():
            objects.append({
                'name': name,
                'short': short,
                'is_set': locale == short
            })

        return jsonify_status_code({objects: objects})

    def put(self, short=None):
        session[LOCALE_KEY] = short
        locale_obj = {
            'short': short,
            'is_set': True,
            'name': current_app.config['LANGUAES'][short]
        }
        return jsonify_status_code(locale_obj, http.ACCEPTED)
