from flask import Blueprint, current_app
from werkzeug.local import LocalProxy


gallery = Blueprint('gallery', __name__, url_prefix='/gallery')
app = LocalProxy(lambda: current_app)
db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)

import api
import models


from .models import album_owner
from flamaster.account.models import User
album_owner(User)
