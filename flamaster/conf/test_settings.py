from .settings import *


DEBUG = True
TESTING = True
# USE_X_SENDFILE = True
SQLALCHEMY_DATABASE_URI = "mysql://root@localhost/test_flamaster"
try:
    from test_local_settings import *
except ImportError:
    pass
