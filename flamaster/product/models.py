from datetime import datetime
from flamaster.app import db
from flamaster.core.utils import slugify
from flamaster.core.models import CRUDMixin


__all__ = ['Product']


class Product(CRUDMixin, db.Model):
    """ By default model inherits id and created_at fields from the CRUDMixin
    """

    __table_args__ = {'extend_existing': True}
    __tablename__ = 'products'

    title = db.Column(db.Unicode(512, convert_unicode=True), nullable=False)
    slug = db.Column(db.String(128), nullable=False, unique=True)
    teaser = db.Column(db.String(1024))
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=True)
    author = db.relationship('User',
                             backref=db.backref('products', lazy='dynamic'))

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            print getattr(self, key)
            setattr(self, key, value)

    def __repr__(self):
        return "<Product: %r>" % self.title

    def save(self, commit=True):
        self.updated_at = datetime.utcnow()
        self.slug = slugify(self.created_at or self.updated_at,
                            self.title, fallback=self.id)
        return super(Product, self).save(commit=commit)

    @classmethod
    def get_by_slug(cls, slug):
        return cls.query.filter_by(slug=slug).first_or_404()


class Price(CRUDMixin, db.Model):
    """ model storage for a price version for end product
    """
    __tablename__ = 'prices'
