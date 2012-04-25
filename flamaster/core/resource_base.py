from flask import session
from flask.views import MethodView


class BaseResource(MethodView):

    @property
    def current_user(self):
        if not session.get('is_anonymous', True):
            return session.get('uid')
        return None

    def __extract_keys(self, data, keys):
        return dict(filter(lambda x: x[0] in keys, data.items()))

    def __exclude_keys(self, data, keys):
        return dict(filter(lambda x: x[0] not in keys, data.items()))
