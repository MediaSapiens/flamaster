from flask.ext.babel import Babel, gettext, ngettext
from flask.ext.cache import Cache
from flask.ext.mail import Mail
from flask.ext.mongoset import MongoSet
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.social import Social, SQLAlchemyConnectionDatastore

babel = Babel()
cache = Cache()
db = SQLAlchemy()
mail = Mail()
mongo = MongoSet()

from flamaster.account.models import User, Role, SocialConnection

security = Security(datastore=SQLAlchemyUserDatastore(db, User, Role))
social = Social(datastore=SQLAlchemyConnectionDatastore(db, SocialConnection))


def register_jinja_helpers(app):
    app.jinja_env.globals.update({
        '_': gettext,
        '__': ngettext
    })
