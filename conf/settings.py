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
RESELLER_ROLE = 'reseller'
ORGANISER_ROLE = 'organiser'
ROLES = [USER_ROLE, ADMIN_ROLE, RESELLER_ROLE, ORGANISER_ROLE]

ACCEPT_LANGUAGES = ['de', 'en', 'ru']

CACHE_TYPE = 'simple'

SQLALCHEMY_DATABASE_URI = "postgresql://user:password@host:port/dbname"
SQLALCHEMY_ECHO = False

# MongoSet configuration ----------------
MONGODB_DATABASE = "fevent"
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
# SOCIAL_APP_URL = "http://fevent.mediasapiens.co/social"
SOCIAL_CONNECT_ALLOW_VIEW = "/account/"
SOCIAL_CONNECT_DENY_VIEW = "/account/"

SPHINX_DIR = 'sphinxdata'

MAP_API_URL = "http://maps.googleapis.com/maps/api/geocode/json"

pictures_path = '/'.join(map(lambda x: str(getattr(datetime.utcnow(), x)),
                                 ['year', 'month', 'day']))
UPLOADS_IMAGES_DIR = '{}/'.format(pictures_path)
UPLOADS_DEFAULT_DEST = os.path.abspath("flamaster/static/uploads")
UPLOADS_DEFAULT_URL = "/static/uploads"

FLICKR_API_KEY = '809d3abac86759d46d3e77f86e82654f'
WIKI_URL = "http://en.wikipedia.org/w/api.php"

PAYMENT_MEHODS = {
    'skrill': {
        'module': 'flamaster.payment.methods.SkrillPaymentMethod'
    },
    'paypal': {
        'module': 'flamaster.payment.methods.PayPalPaymentMethod'
    },
    'card': {
        'module': 'flamaster.payment.methods.CardPaymentMethod'
    },
    'bank transfer': {
        'module': 'flamaster.payment.methods.BankPaymentMethod'
    }
}

#FLICKR_API_SECRET = '2c81c7c12491ae4e'
##YOUTUBE_DEVELOPER_KEY = 'AI39si6bveFM4rV7I4p-7dD73ZpO5KE2qLxAMReqvWkcLSJ7ZZtNdMtjQm-fKvFYZKg8FfLXKAL9vyzIaESimZR4R_QT5atgvA'
##YOUTUBE_CLIENT_ID = 'fevent_id'
#YOUTUBE_API_KEY = 'AIzaSyChBit_-W404d-88vvpwxbrOJ-5SekxK9I'
#YOUTUBE_API_SECRET = '8M8bjG4UNlJuJB6SJLM77EUl'

try:
    ls = importlib.import_module('flamaster.conf.local_settings')
    for attr in dir(ls):
        if '__' not in attr:
            setattr(sys.modules[__name__], attr, getattr(ls, attr))
except ImportError:
    print "local_settings undefined"
