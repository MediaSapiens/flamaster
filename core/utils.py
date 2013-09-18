# -*- coding: utf-8 -*-
import re
import types
import uuid

from bson import ObjectId
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP

from flask import current_app, render_template, request
from flask.ext.mail import Message
from flask import json
from flask.ext.babel import lazy_gettext as _

from importlib import import_module
from os.path import abspath, dirname, join
from speaklater import _LazyString
from unidecode import unidecode
from werkzeug import import_string, cached_property
import trafaret as t

from . import mail


class LazyView(object):

    def __init__(self, import_name, endpoint=None):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name
        self.endpoint = endpoint

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)

    @cached_property
    def view(self):
        return import_string(self.import_name)


class LazyResource(LazyView):

    @cached_property
    def view(self):
        return import_string(self.import_name).as_view(self.endpoint)


def add_api_rule(bp, endpoint, pk_def, import_name):
    resource = LazyResource(import_name, endpoint)
    collection_url = "/{}/".format(endpoint)
    # collection endpoint

    pk = pk_def.keys()[0]
    pk_type = pk_def[pk] and pk_def[pk].__name__ or None

    if pk_type is None:
        item_url = "%s<%s>" % (collection_url, pk)
    else:
        item_url = "%s<%s:%s>" % (collection_url, pk_type, pk)

    bp.add_url_rule(collection_url, view_func=resource,
                    methods=['GET', 'POST'])
    bp.add_url_rule(item_url, view_func=resource,
                    methods=['GET', 'PUT', 'DELETE'])


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
lazy_cascade = {'lazy': 'dynamic', 'cascade': 'all'}


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.ctime()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, _LazyString):
            return unicode(obj)
        if hasattr(obj, 'as_dict'):
            return obj.as_dict()
        return super(CustomEncoder, self).default(obj)


def json_dumps(data):
    try:
        return json.dumps(data, indent=2, cls=CustomEncoder)
    except ValueError as e:
        current_app.logger.debug("%s: %s", e.message, data)
        raise e


def jsonify_status_code(data=None, status=200, mimetype='application/json'):
    data = data or {}

    return current_app.response_class(json_dumps(data),
        status=status, mimetype=mimetype)


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


plural_underscored = lambda s: plural_name(underscorize(s))


def send_email(subject, recipient, template, callback=None, **context):
    """ Send an email via the Flask-Mail extension.

    :param subject: Email subject
    :param recipient: Email recipient
    :param template: The name of the email template
    :param context: The context to render the template with
    """

    # context.setdefault('security', _security)
    # context.update(_security._run_ctx_processor('mail'))
    recipients = isinstance(recipient, basestring) and [recipient] or recipient
    msg = Message(subject, recipients=recipients)
    site_url = '{scheme}://{route}'.format(
                scheme=request.scheme,
                route=current_app.config['SERVER_HOST']
            )
    context.update({'site_url': site_url})

    ctx = ('email', template)
    msg.body = render_template('{0}/{1}.txt'.format(*ctx), **context)
    msg.html = render_template('{0}/{1}.html'.format(*ctx), **context)
    if hasattr(callback, '__call__'):
        msg = callback(msg)
    # if _security._send_mail_task:
    #     _security._send_mail_task(msg)
    #     return
    mail.send(msg)


def round_decimal(dec_value):
    """
    A routine to standardize rounding of decimal numbers to the format we expect
    """
    if type(dec_value) != Decimal:
        raise Exception('Expected a decimal value')
    return dec_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def null_fields_filter(fields=[], data=None):
    if data is None:
        return None

    for field in fields:
        if data.get(field, '') in (None, 'null'):
            data.pop(field)

    return data

def trafaret_translate(error):
    print error.__dict__
    def _replace(err):
        for k, v in err.iteritems():
            error = getattr(v, 'error', None)
            if error is None:
                pass
            elif type(error) == dict:
                v.error = _replace(error)
            elif error == 'value is not a valid email address':
                v.error = _('Value is not a valid email address')
            elif error == 'blank value is not allowed':
                v.error = _('Blank value is not allowed')
            elif error == 'value can\'t be converted to int':
                v.error = _('Value can\'t be converted to int')
            elif error == 'value should be None':
                v.error = _('Value should be None')
            elif error == 'is required':
                v.error = _('Is required')

            err[k] = v

        return err

    error.error = _replace(error.error)

    return error

