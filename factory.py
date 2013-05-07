from __future__ import absolute_import
import os
import time
import uuid

from datetime import datetime
from flask import Flask, abort, g, request, session, render_template
from flask.ext.babel import get_locale as babel_locale

import logging
from logging.handlers import SMTPHandler

from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import import_string

from flamaster.core import http
from flamaster.core.session import RedisSessionInterface
from flamaster.extensions import register_jinja_helpers


class ExtensionLoadError(Exception):
    pass


class BlueprintLoadError(Exception):
    pass


class AppFactory(object):
    """ Application factory for creating flask instance serving this project.
        Usage:
            app = AppFactory('settings').init_app(__name__)
    """
    def __init__(self, config, envvar='PROJECT_SETTINGS', bind_db_object=True):
        self.app_config = config
        self.app_envvar = os.environ.get(envvar, False)
        # self.bind_db_object = bind_db_object

    def init_app(self, app_name, **kwargs):
        app = Flask(app_name, **kwargs)
        app.config.from_object(self.app_config)
        app.config.from_envvar(self.app_envvar, silent=True)

        self._add_logger(app)
        self._bind_extensions(app)
        self._register_blueprints(app)
        self._register_hooks(app)

        app.session_interface = RedisSessionInterface()
        app.wsgi_app = ProxyFix(app.wsgi_app)
        return app

    def _import(self, path):
        module_name, object_name = path.rsplit('.', 1)
        module = import_string(module_name)
        return module, object_name

    def _bind_extensions(self, app):
        for ext_path in app.config.get('EXTENSIONS', []):
            module, ext_name = self._import(ext_path)

            try:
                ext = getattr(module, ext_name)
            except AttributeError:
                ExtensionLoadError("Extension '{}'' not found".format(ext))

            try:
                ext.init_app(app)
            except AttributeError:
                ext(app)

    def _register_blueprints(self, app):
        """ Register all blueprint modules listed under the settings
            BLUEPRINTS key """
        for blueprint_path in app.config.get('BLUEPRINTS', []):
            module, bp_name = self._import(blueprint_path)
            if hasattr(module, bp_name):
                app.register_blueprint(getattr(module, bp_name))
            else:
                raise BlueprintLoadError('No {} blueprint '
                                         'found'.format(bp_name))

    def _register_hooks(self, app):
        register_jinja_helpers(app)
        app.before_request(setup_session)
        app.errorhandler(http.NOT_FOUND)(show_page_not_found)
        app.errorhandler(http.INTERNAL_ERR)(show_internal_error)
        app.after_request(modify_headers)
        app.extensions['babel'].localeselector(get_locale(app))

    def _add_logger(self, app):
        """ Creates SMTPHandler for logging errors to the specified admins list
        """
        kwargs = dict()
        username = app.config.get('MAIL_USERNAME')
        password = app.config.get('MAIL_PASSWORD')

        if username and password:
            kwargs['credentials'] = (username, password)

        mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                                   app.config['DEFAULT_MAIL_SENDER'],
                                   app.config['ADMINS'],
                                   '[ERROR] Findevent got error',
                                   **kwargs)

        mail_handler.setFormatter(logging.Formatter('''
            Message type:       %(levelname)s
            Location:           %(pathname)s:%(lineno)d
            Module:             %(module)s
            Function:           %(funcName)s
            Time:               %(asctime)s

            Message:

            %(message)s
        '''))

        mail_handler.setLevel(logging.DEBUG)

        if not app.debug:
            app.logger.addHandler(mail_handler)

def modify_headers(response):
    headers = [
        ('Cache-Control',
            'public, no-store, max-age=0'),
        ('Access-Control-Allow-Origin',
            '*'),
        ('Access-Control-Allow-Methods',
            'GET,POST,PUT,DELETE,HEAD,OPTIONS'),
        ('Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept,'
            ' X-HTTP-Method-Override'),
    ]
    map(lambda h: response.headers.add(*h), headers)
    return response


def setup_session():
    g.now = time.mktime(datetime.utcnow().timetuple())
    g.locale = babel_locale().language


def show_internal_error(error):
    return render_template('50x.html'), http.INTERNAL_ERR


def show_page_not_found(error):
    try:
        return render_template('base.html'), http.NOT_FOUND
    except:
        return abort(http.NOT_FOUND)


def get_locale(app):

    def closure():
        languages = app.config['ACCEPT_LANGUAGES']
        matched = request.accept_languages.best_match(languages)
        language = session.get(app.config['LOCALE_KEY'], matched)
        return language

    return closure
