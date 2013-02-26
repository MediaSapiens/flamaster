from flask import Blueprint
from flask.ext.security import SQLAlchemyUserDatastore
from flask.ext.social import SQLAlchemyConnectionDatastore
from flamaster.extensions import db

from .models import User, Role, SocialConnection


user_ds = SQLAlchemyUserDatastore(db, User, Role)
connection_ds = SQLAlchemyConnectionDatastore(db, SocialConnection)

bp = Blueprint('account', __name__, url_prefix='/account')

import signals, api
