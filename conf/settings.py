import importlib
import sys

DEBUG = True
SECRET_KEY = "<your secret key>"
USE_X_SENDFILE = True
CSRF_ENABLED = True
# SESSION_COOKIE_SECURE = True

ADMINS = ('admin@example.com', 'sfelde@mediasapiens.co',
          'yehor@mediasapiens.co')

USER_ROLE = 'user'
ADMIN_ROLE = 'admin'
ORGANIZER_ROLE = 'organizer'

ROLES = [USER_ROLE, ADMIN_ROLE, ORGANIZER_ROLE]

ACCEPT_LANGUAGES = ['de', 'en']
LANGUAGES = {
    'en': u'English',
    'de': u'Deutsch'
}
BABEL_DEFAULT_LOCALE = 'de'
LOCALE_KEY = 'locale'

CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 900  # defult timeout is 15 minutes

SQLALCHEMY_DATABASE_URI = "postgresql://user:password@host:port/dbname"
SQLALCHEMY_ECHO = False

# MongoSet configuration ----------------
MONGODB_DATABASE = ""
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_AUTOREF = True
MONGODB_AUTOINCREMENT = False
MONGODB_FALLBACK_LANG = BABEL_DEFAULT_LOCALE
# ----------------

MIGRATIONS_REPOSITORY = 'migrations'

DEFAULT_PAGE_SIZE = 100
# Flask-Mail sender for default email sender
DEFAULT_ALBUM_COVERAGE = None  # image/defaut/album_coverage
# TODO: for flask-mail:
DEFAULT_MAIL_SENDER = "<no-reply@findevent.de>"

MAIL_FAIL_SILENTLY = True

PAYMENT_METHODS = {
    'skrill': {
        'module': 'flamaster.payment.methods.SkrillPaymentMethod'
    },
    'paypal': {
        'module': 'flamaster.payment.methods.paypal.PayPalPaymentMethod',
        'SANDBOX': True,
        'settings': {
            'USER': '<paypal user>',
            'PWD': '<paypal password>',
            'SIGNATURE': '<paypal signature>',
            'VERSION': '<api version>',
        }
    },
    'klarna': {
        'module': 'flamaster.payment.methods.klarna.KlarnaPaymentMethod',
        'SANDBOX': True
    },
    'groupon': {
        'module': 'flamaster.payment.methods.groupon.GrouponPaymentMethod',
        'SANDBOX': True,
        'settings': {
            'endpoint': 'http://api.groupon.de/api/v1/{path}',
            'consumer': '<consumer merchantId>',
            'name': '<consumer login>',
            'password': '<consumer password>',
        }
    },
    'card': {
        'module': 'flamaster.payment.methods.CardPaymentMethod'
    },
    'bank transfer': {
        'module': 'flamaster.payment.methods.BankPaymentMethod'
    }
}

SHOP_ID = '1'
# Flask-Security settings for default email sender
SECURITY_EMAIL_SENDER = DEFAULT_MAIL_SENDER
# either user should confirm email after registration or no
SECURITY_CONFIRMABLE = True
SECURITY_RECOVERABLE = True
SECURITY_TRACKABLE = True

SECURITY_CONFIRM_URL = "/account/activate"
SECURITY_LOGOUT_URL = "/account/signout"
SECURITY_POST_LOGIN_VIEW = "/account/"
SECURITY_POST_CONFIRM_VIEW = "/account/"

SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_PASSWORD_SALT = ')(*ENB%WOI3j3kf'

SOCIAL_URL_PREFIX = "/social"

SOCIAL_CONNECT_ALLOW_VIEW = "/account/"
SOCIAL_CONNECT_DENY_VIEW = "/account/"

THUMBNAIL_UPSCALE = False
THUMBNAIL_FORMAT = 'PNG'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~Payment settings~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


DELIVERY_OPTIONS = {
    'standard': {
        'module': 'flamaster.delivery.methods.StandardDelivery',
    },
    'express': {
        'module': 'flamaster.delivery.methods.ExpressDelivery',
    },
    'download': {
        'module': 'flamaster.delivery.methods.PerProductDownload',
        'default': True
    }
}

try:
    ls = importlib.import_module('flamaster.conf.local_settings')
    for attr in dir(ls):
        if '__' not in attr:
            setattr(sys.modules[__name__], attr, getattr(ls, attr))
except ImportError:
    print "local_settings undefined"
