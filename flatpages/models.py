# encoding: utf-8
from flamaster.core import db
from flamaster.core.models import CRUDMixin


class FlatPage(db.Model, CRUDMixin):
    """ A flatpage representation model
    """
    name = db.Column(db.Unicode(512), nullable=False)
    slug = db.Column(db.String(256), nullable=False, unique=True)
    content = db.Column(db.UnicodeText)
    template_name = db.Column(db.Unicode(512))
    registration_required = db.Column(db.Boolean, default=False)
