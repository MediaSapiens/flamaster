from flask import session
from flask.views import MethodView


class BaseResource(MethodView):

    @property
    def current_user(self):
        if not session.get('is_anonymous', True):
            return session.get('uid')
        return None
