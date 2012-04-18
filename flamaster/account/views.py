from flask import flash, request, redirect, render_template, url_for, abort

from flamaster.core.utils import send_email, change_password_validate

from . import account
from .models import User
import trafaret as t

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
    if len(request.form):
        d = t.Dict(password=t.String, password_confirm=t.String).append(
            change_password_validate)
        d.check({'password': request.form.get('password', None),
                 'password_confirm': request.form.get(
                     'password_confirm', None)})
        user.set_password(request.form.get('password'))
        user.save()
    return render_template('password_reset_confirm.html', token=token)
