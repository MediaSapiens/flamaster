from datetime import datetime
from flamaster.app import db
from flamaster.core.utils import slugify
from flamaster.core.models import CRUDMixin


__all__ = ['Product']


class Product(db.Model, CRUDMixin):
    __tablename__ = 'products'

    title = db.Column(db.String(512), nullable=False)
    slug = db.Column(db.String(128), nullable=False, unique=True)
    teaser = db.Column(db.String(1024))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User',
                             backref=db.backref('products', lazy='dynamic'))

    def __init__(self, **kwargs):
        assert 'title' in kwargs
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def __repr__(self):
        return "<Product: %r>" % self.title

    def save(self, commit=True):
        self.slug = slugify(self.created_at or self.updated_at, self.title)
        return super(Product, self).save(commit=commit)

    @classmethod
    def get_by_slug(cls, slug):
        return cls.query.filter_by(slug=slug).first_or_404()


class Price(db.Model, CRUDMixin):
    """ model storage for a price version for end product
    """
    __tablename__ = 'prices'
