from flask import flash, request, redirect, render_template, url_for, abort

from flamaster.core.utils import send_email

from . import account
from .models import User

__all__ = ['request_reset', 'confirm_reset']


@account.route('/reset/', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST' and request.form.get('email'):
        user = User.query.filter_by(email=request.form.get('email')).first_or_404()

        token = user.create_token()
        # Create the message
        send_email(to=request.form['email'],
                   subject="You've requested a password reset",
                   body=render_template("email_reset.html", token=token))
        flash("We sent you an email with the special link to restore "
              "your password", 'success')
        return redirect(url_for('.request_reset'))
    return render_template('password_reset_request.html')


@account.route('/reset/<token>/', methods=['GET', 'POST'])
def confirm_reset(token):
    user = User.validate_token(token) or abort(403)
    password = request.form.get('password', None)
    password_confirm = request.form.get('password_confirm', None)
    if password and password_confirm and password == password_confirm:
        user.set_password(password)
    return render_template('password_reset_confirm.html', token=token)
