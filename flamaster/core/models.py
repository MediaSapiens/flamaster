from datetime import datetime

from sqlalchemy.orm import class_mapper
from flamaster.app import db


class CRUDMixin(object):
    """ Basic CRUD mixin
    """

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def get(cls, id):
        if id is not None:
            return cls.query.get(id)
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        commit and db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        commit and db.session.commit()

    def as_dict(self):
        """ method for building dictionary for model value-properties filled
            with data from mapped storage backend
        """
        omit_values = ['password']
        return dict((c.name, getattr(self, c.name))
              for c in class_mapper(self.__class__).mapped_table.c
              if c.name not in omit_values)
