from flask import flash, request, redirect, render_template, url_for, abort
import trafaret as t

from flamaster.core.utils import send_email, validate_password_change

from . import account
from .models import User

__all__ = ['request_reset', 'confirm_reset']


@account.route('/reset/', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST' and request.form.get('email'):
        user = User.query.filter_by(email=request.form['email']).first_or_404()
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

    if len(request.form) and request.method == 'POST':
        try:
            validate_password_change(request.form.to_dict())
        except t.DataError as e:
            return render_template('password_reset_confirm.html',
                                   token=token, error=e)

        user.set_password(request.form['password']).save()
        return redirect(url_for('core.index'))

    return render_template('password_reset_confirm.html', token=token)
