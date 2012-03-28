DEBUG = True
SECRET_KEY = "ZmxhbWFzdGVyMzEybmltbnVsbEBmb3gtbGFwdG9wOnN0YXRpYyQgY29tcGFzcyBjb21waWxl"
# SESSION_COOKIE_SECURE = True
# USE_X_SENDFILE = True
SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost/flamaster"
SQLALCHEMY_ECHO = True

try:
    from local_settings import *
except ImportError:
    pass
