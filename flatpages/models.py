# encoding: utf-8
from flamaster.core.models import SlugMixin
from flamaster.core.utils import slugify

from sqlalchemy.ext.hybrid import hybrid_property

from flamaster.extensions import db


class FlatPage(db.Model, SlugMixin):
    """ A flatpage representation model
    """
    content = db.Column(db.UnicodeText)
    template_name = db.Column(db.Unicode(512))
    registration_required = db.Column(db.Boolean, default=False)

    @hybrid_property
    def slug(self):
        return self._slug

    @slug.setter
    def slug(self, name):
        self._slug = slugify(name, prefix=False)

    def save(self, commit=True):
        if not self.slug:
            return super(FlatPage, self).save(commit)
        return super(SlugMixin, self).save(commit)

# TODO: if we change flatpage.name, what will happen with slug???
