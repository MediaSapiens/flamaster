from flask import Blueprint, current_app


bp = Blueprint('gallery', __name__, url_prefix='/gallery')


import models, api, views
