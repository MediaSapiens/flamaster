from flask import request
from flask import render_template
from sqlalchemy.orm.exc import NoResultFound

import smtplib
import email.utils
from email.mime.text import MIMEText

from .models import User
from .api import account

OUR_EMAIL = 'author@example.com'

__all__ = ['edit_person', 'password_reset', 'validation_token']


@account.route('/edit/<id>/', methods=['GET', 'POST'])
def edit_person(id):
    user = User.query.get_or_404(id)
    return render_template('edit_user.html')


@account.route('/password_reset/', methods=['GET', 'POST'])
def password_reset():
    #print dir(request), request.form.to_dict()
    data = request.form.to_dict()
    if 'email' in data:
        try:
            user = User.query.filter_by(email=data['email']).one()
        except NoResultFound:
            return 'Thees email no found'

        token = user#.create_token()
        # Create the message
        msg = MIMEText('This is the body of the message.')
        msg['To'] = email.utils.formataddr(('Recipient', data['email']))
        msg['From'] = email.utils.formataddr(('Author', OUR_EMAIL))
        msg['Subject'] = 'message {}'.format(token)

        server = smtplib.SMTP('127.0.0.1', 1025)
        server.set_debuglevel(True) # show communication with the server
        try:
            server.sendmail(OUR_EMAIL, [data['email']], msg.as_string())
        finally:
            server.quit()

        return render_template('edit_user.html')


@account.route('/validation_token/<token>/', methods=['GET', 'POST'])
def validation_token(token):
    if User.create_token(token):
        return render_template('edit_user.html')
