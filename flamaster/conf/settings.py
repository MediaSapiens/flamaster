DEBUG = False
SECRET_KEY = "ZmxhbWFzdGVyMzEybmltbnVsbEBmb3gtbGFwdG9wOnN0YXRpYyQgY29tcGFzcyBjb21waWxl"
USE_X_SENDFILE = True
# SESSION_COOKIE_SECURE = True

SQLALCHEMY_DATABASE_URI = "mysql://flamaster@localhost.localdomain/flamaster"
SQLALCHEMY_ECHO = False

DEFAULT_MAIL_SENDER = "<noreply@findevent.com>"
MAIL_FAIL_SILENTLY = True

try:
    from local_settings import *
except ImportError:
    pass
