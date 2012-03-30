from flask import render_template
from flask import Blueprint


account = Blueprint('account', __name__, template_folder='templates',
                    url_prefix='/account')

#__all__ = ['index', 'account']

@account.route('/')
def index():
    return render_template('account/index.html')
