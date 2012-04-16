from flask import request, url_for
from flask import render_template
from sqlalchemy.orm.exc import NoResultFound

from .models import User
from .api import account

from flamaster.app import mail
from flaskext.mail import Message

__all__ = ['edit_person', 'password_reset', 'validation_token']


@account.route('/edit/<id>/', methods=['GET', 'POST'])
def edit_person(id):
#    user = User.query.get_or_404(id)
    return render_template('edit_user.html')


@account.route('/password_reset/', methods=['GET', 'POST'])
def password_reset():
    # print dir(request), request.data
    if request.method == 'POST':
        data = request.form.to_dict()
        if 'email' in data:
            try:
                user = User.query.filter_by(email=data['email']).one()
            except NoResultFound:
                return 'This email no found'

            token = user.create_token()
            msg = Message('This is the body of the message.',
                          recipients=[data['email']])
            msg.html = '<b>link for password reset http://127.0.0.1:5000{}'.format(
                url_for('.validation_token', **{'token': token}))
            mail.send(msg)

    return render_template('edit_user.html')


@account.route('/validation_token/<token>/', methods=['GET', 'POST'])
def validation_token(token):
    if User.validate_token(token):
        return render_template('edit_user.html')
