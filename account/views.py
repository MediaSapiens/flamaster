from flask import redirect
from flask.ext.security.recoverable import reset_password_token_status

from flamaster.core import core

@core.route('/reset_password/<token>')
def reset_password(token):
    expired, invalid, user = reset_password_token_status(token)
    if invalid or expired:
        return redirect('/?redirect_from=forgot_password&status=error')
    return redirect('/?redirect_from=forgot_password&status=success&token=%s' % token)

