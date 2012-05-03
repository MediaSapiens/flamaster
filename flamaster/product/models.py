from datetime import datetime
from flamaster.app import db
from flamaster.core.utils import slugify, CRUDMixin


__all__ = ['Product']


class Product(db.Model, CRUDMixin):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'product'

    title = db.Column(db.Unicode(512, convert_unicode=True), nullable=False)
    slug = db.Column(db.Unicode(128, convert_unicode=True), nullable=False, unique=True)
    teaser = db.Column(db.String(1024))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Product: %r>" % self.title

    def save(self, commit=True):
        self.updated_at = datetime.utcnow()
        self.slug = slugify(self.created_at or self.updated_at,
                            self.title, fallback=self.id)
        db.session.add(self)
        commit and db.session.commit()
        return super(Product, self).save(commit=commit)
