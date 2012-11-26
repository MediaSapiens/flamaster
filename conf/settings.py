from datetime import datetime
import importlib
import sys
import os

DEBUG = True
SECRET_KEY = "<your secret key>"
USE_X_SENDFILE = True
CSRF_ENABLED = True
# SESSION_COOKIE_SECURE = True

ADMINS = ('admin@example.com', )

USER_ROLE = 'user'
ADMIN_ROLE = 'admin'
ORGANIZER_ROLE = 'organizer'

ROLES = [USER_ROLE, ADMIN_ROLE, ORGANIZER_ROLE]

ACCEPT_LANGUAGES = ['de', 'en', 'ru']

CACHE_TYPE = 'simple'

SQLALCHEMY_DATABASE_URI = "postgresql://user:password@host:port/dbname"
SQLALCHEMY_ECHO = False

# MongoSet configuration ----------------
MONGODB_DATABASE = ""
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_AUTOREF = True
MONGODB_AUTOINCREMENT = False
MONGODB_FALLBACK_LANG = 'en'
# ----------------
DEFAULT_PAGE_SIZE = 100
# Flask-Mail sender for default email sender
DEFAULT_EMAIL_FROM = "<fevent@mediasapiens.co>"
#TODO: add default album coverage
DEFAULT_ALBUM_COVERAGE = None  # image/defaut/album_coverage

MAIL_FAIL_SILENTLY = True
# TODO: for flask-mail:
DEFAULT_MAIL_SENDER = DEFAULT_EMAIL_FROM
# Flask-Security settings for default email sender
SECURITY_EMAIL_SENDER = DEFAULT_EMAIL_FROM
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

pictures_path = '/'.join(map(lambda x: str(getattr(datetime.utcnow(), x)),
                                 ['year', 'month', 'day']))
UPLOADS_IMAGES_DIR = '{}/'.format(pictures_path)
UPLOADS_DEFAULT_DEST = os.path.abspath("flamaster/static/uploads")
UPLOADS_DEFAULT_URL = "/static/uploads"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~Payment settings~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    'card': {
        'module': 'flamaster.payment.methods.CardPaymentMethod'
    },
    'bank transfer': {
        'module': 'flamaster.payment.methods.BankPaymentMethod'
    }
}

DELIVERY_OPTIONS = {
    'standard': 'flamaster.delivery.methods.StandardDelivery',
    'express': 'flamaster.delivery.methods.ExpressDelivery',
    'download': 'flamaster.delivery.methods.PerProductDownload'
}

try:
    ls = importlib.import_module('city_lang.settings_local')
    for attr in dir(ls):
        if '__' not in attr:
            setattr(sys.modules[__name__], attr, getattr(ls, attr))
except ImportError:
    print "settings_local undefined"
