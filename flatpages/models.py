# encoding: utf-8
from flask import current_app

from flamaster.core import db
from flamaster.core.models import CRUDMixin
from flamaster.core.decorators import multilingual


@multilingual
class FlatPage(db.Model, CRUDMixin):
    """ A flatpage representation model
    """
    shop_id = db.Column(db.String(128), default=current_app.config['SHOP_ID'])
    name = db.Column(db.Unicode(512), nullable=False)
    slug = db.Column(db.String(256), nullable=False, unique=True)
    content = db.Column(db.UnicodeText)
    template_name = db.Column(db.Unicode(512))
    registration_required = db.Column(db.Boolean, default=False)
