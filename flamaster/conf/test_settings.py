from .settings import *


DEBUG = True
TESTING = True
# USE_X_SENDFILE = True
SQLALCHEMY_DATABASE_URI = "mysql://root@localhost/test_flamaster"
try:
    from local_test_settings import *
except ImportError:
    pass
