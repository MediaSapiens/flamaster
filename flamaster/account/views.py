from flask import request, render_template, current_app
from flask.ext.mail import Message

from . import account
from .models import User

__all__ = ['request_reset', 'confirm_reset']


@account.route('/reset/', methods=['GET', 'POST'])
def request_reset():
    #print dir(request), request.form.to_dict()
    if len(request.form):
        user = User.query.filter_by(email=request.form.get('email')).first_or_404()

        token = user.create_token()
        # Create the message
        msg = Message(subject="You've requested a password reset",
                      body=render_template("email_reset.html", token=token),
                      recipients=request.form['email'])
        app = current_app._get_current_object()
        app.mail.send(msg)

    return render_template('request_password_reset.html')


@account.route('/reset/<token>/', methods=['GET', 'POST'])
def confirm_reset(token):
    if User.validate(token):
        return render_template('confirm_password_reset.html')
