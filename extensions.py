from __future__ import absolute_import
from flask.ext.babel import Babel, gettext, ngettext

from flask.ext.mail import Mail
from flask.ext.mongoengine import MongoEngine

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security



def register_jinja_helpers(app):
    app.jinja_env.globals.update({
        '_': gettext,
        '__': ngettext
    })


babel = Babel()

try:
    from flask.ext.cache import Cache
    cache = Cache()
except ImportError:
    cache = None

db = SQLAlchemy()
mail = Mail()
mongo = MongoEngine()


try:
    from flask.ext.redis import Redis
    redis = Redis()
except ImportError:
    redis = None

security = Security()

try:
    from flask.ext.social import Social
    social = Social()
except ImportError:
    social = None

try:
    from flask.ext.elasticsearch import ElasticSearch
    es = ElasticSearch()
except ImportError:
    es = None



