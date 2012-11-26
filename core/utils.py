# -*- coding: utf-8 -*-
import re
import types
import uuid
from bson import ObjectId
from datetime import datetime

from flask import current_app, abort
from flask.ext.mail import Message
from flask.helpers import json

from functools import wraps
from importlib import import_module
from os.path import abspath, dirname, join
from speaklater import _LazyString
from unidecode import unidecode
from werkzeug import import_string, cached_property


class LazyResource(object):

    def __init__(self, import_name, endpoint):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name
        self.endpoint = endpoint

    @cached_property
    def view(self):
        return import_string(self.import_name).as_view(self.endpoint)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
lazy_cascade = {'lazy': 'dynamic', 'cascade': 'all'}


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.ctime()
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, _LazyString):
            return unicode(obj)
        if hasattr(obj, 'as_dict'):
            return obj.as_dict()
        return super(CustomEncoder, self).default(obj)


def json_dumps(data):
    return json.dumps(data, indent=2, cls=CustomEncoder)


def jsonify_status_code(data=None, status=200):
    data = data or {}

    return current_app.response_class(json_dumps(data),
        status=status, mimetype='application/json')


def slugify(text, separator='-', prefix=True):
    text = unidecode(smart_str(text))
    text = re.sub('[^\w\s]', '', text)
    text = re.sub('[^\w]', separator, text)
    if prefix:
        hsh = uuid.uuid4().hex[:4]
        text = '%s%s%s' % (text, separator, hsh)
    return text.lower()


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """ Returns a bytestring version of 's', encoded as specified in
        'encoding'. If strings_only is True, don't convert (some)
        non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    elif not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


def resolve_class(class_path):
    """ helper method for importing class by class path string repesentation
    """
    module_name, class_name = class_path.rsplit('.', 1)
    return getattr(import_module(module_name), class_name)


def rules(language):
    """ helper method for getting plural form rules from the text file
    """
    rule_file = join(dirname(abspath(__file__)), 'rules.%s') % language
    for line in file(rule_file):
        pattern, search, replace = line.split()
        yield lambda word: re.search(pattern, word) and \
                re.sub(search, replace, word)


def plural_name(noun, language='en'):
    """ pluralize a noun for the selected language
    """
    for applyRule in rules(language):
        result = applyRule(noun)
        if result:
            return result


def underscorize(name):
    """ Converts CamelCase notation to the camel_case
    """
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def send_email(to, subject, body):
    """ Helper that wraps email sending atoms in
        Flask-Mail calls
    """
    recipients = isinstance(to, basestring) and [to] or to
    msg = Message(subject=subject, body=body, recipients=recipients)
    current_app.mail.send(msg)


class Permissions(object):
    """Multiton. Stores permissions names.
    Call the permission instance by name.
    Permission is a function contains any user actions decorated in permissions
    register decorator.
    """
    _instances = {}

    def register(self, permission):
        """Register permissions
        """
        if permission.__name__ not in self._instances:
            self._instances[permission.__name__] = permission
        return permission

    def check_permission(self, perm_name, *perm_args, **perm_kwargs):
        """Check permission decorator
        """
        allowed = self._instances[perm_name]

        def wrap(f=None):

            if getattr(f, '__call__', False):

                @wraps(f)
                def closure(*args, **kwargs):
                    # extending permission method with the decorated method
                    # argumants and  keyword arguments
                    new_args = perm_args + args
                    perm_kwargs.update(kwargs)

                    check_result = allowed(*new_args, **perm_kwargs)

                    return check_result and f(*args, **kwargs) or abort(403)

                return closure

            return allowed(*perm_args, **perm_kwargs)

        return wrap


permissions = Permissions()
check_permission = permissions.check_permission
plural_underscored = lambda noun: plural_name(underscorize(noun))
