# encoding: utf-8
import gridfs
import os

from flamaster.core.models import CRUDMixin, BaseMixin

from sqlalchemy import func
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy.ext.declarative import declared_attr

from .utils import filter_wrapper, dict_obj
from . import db, mongo

__all__ = ['Image', 'Album']


class GalleryMixin(CRUDMixin):
    """Base mixin for Gallery objects
    """
    name = db.Column(db.Unicode(512), nullable=False, default=u'')
    description = db.Column(db.UnicodeText, nullable=False, default=u'')
    is_public = db.Column(db.Boolean, default=True)

    @declared_attr
    def author_id(cls):
        return db.Column(
                db.Integer, db.ForeignKey("users.id"), nullable=False)

    @declared_attr
    def author(cls):
        return db.relationship('User',
                               backref=db.backref(cls.__tablename__,
                                                  lazy='dynamic'))

    def __repr__(self):
        return "<%s:%s>" % (self.__class__.__name__,
                            self.name)


class Album(db.Model, GalleryMixin):

    api_fields = ['id', 'name', 'description', 'coverage', 'total_images']

    def __init__(self, **kwargs):
        if 'owner' in kwargs:
            self.owner = kwargs.pop('owner')
        super(Album, self).__init__(**kwargs)

    @hybrid_property
    def coverage(self):
        image = self.images.filter_by(is_coverage=True)
        if image.count() == 0:
            image = self.images.order_by(func.random()).limit(1)

        image = image.first()
        return image and {'url': image.url, 'id': image.id} or None

    @coverage.setter
    def coverage(self, value):
        image = self.images.filter_by(id=value['id']).first()
        if image is not None:
            self.coverage and self.coverage.update(is_coverage=False)
            image.update(is_coverage=True)

    @property
    def public_images(self):
        return self.images.filter_by(is_public=True)

    # TODO: show all images to the owner and administrative roles
    @property
    def total_images(self):
        return self.public_images.count()

    def delete(self, commit=True):
        for image in self.images.all():
            image.delete()
        return super(Album, self).delete()

    @classmethod
    def create_defaults(cls, user):
        """ Ensure or create 2 albums for user with names 'default' and
            'userpic'
        """
        pass
        # if Album.query.filter_by(owner=kwargs['author_id']).count() == 0:
        #     Album.create(name='default', author_id=kwargs['author_id'])
        #     Album.create(name='userpic', author_id=kwargs['author_id'])

        # # TODO: understand how does it works with id of foreign object?
        # if 'album_id' not in kwargs:
        #     default_album = Album.query.filter_by(name='default').first().id
        #     kwargs['album_id'] = default_album


class Image(db.Model, GalleryMixin):
    fullpath = db.Column(db.Unicode(512), nullable=False, index=True)
    url = db.Column(db.Unicode(512), nullable=False, index=True)
    is_coverage = db.Column(db.Boolean, default=False)
    album_id = db.Column(db.Integer, db.ForeignKey("albums.id"))
    album = db.relationship('Album', backref=db.backref('images',
                            cascade='all, delete-orphan', lazy='dynamic'))

    @property
    def filename(self):
        return os.path.basename(self.fullpath)

    @classmethod
    def create(cls, image, content_type, **kwargs):
        gridfs_session = gridfs.GridFS(mongo.session)
        file_id = gridfs_session.put(image, content_type=content_type)
        kwargs.update({
            'fullpath': unicode(file_id),
            'url': 'gridfs'
        })
        # TODO: completely rewrite uploads
        # uploaded_images = UploadSet('images', IMAGES)
        # configure_uploads(current_app, uploaded_images)
        # folder = current_app.config['UPLOADS_IMAGES_DIR']
        # filename = uploaded_images.save(image, folder=folder)
        # name = create_name(image.filename)
        # kwargs.update({'fullpath': uploaded_images.path(filename),
        #                'url': uploaded_images.url(filename),
        #                'name': kwargs.get('name', name)})
        return cls(**kwargs).save()

    # TODO:  where does it use???
    def copy_to(self, album_id):
        image_data = self.as_dict()
        removal = set(('id', 'album_id'))
        image_data = dict((attr, image_data[attr])
                          for attr in image_data.viewkeys() - removal)
        return Image(album_id=album_id, **image_data).save()

    def delete(self):
        if Image.query.filter_by(fullpath=self.fullpath).count() == 1:
            os.remove(self.fullpath)
        return super(Image, self).delete()

    def access(self, uid):
        return self.is_public or self.author_id == uid or False


class GenericOwnerComparator(Comparator):
    """Comparator for generic foreign key slaves
    """
    def __eq__(self, other):
        return self.expression.has(owner_id=other.id,
                                   owner_table=other.__tablename__)

    def __ne__(self, other):
        return db.not_(self.__eq__(other))


class SlaveComparator(GenericOwnerComparator):
    """Comparator for owners witch have relation
       on slave with generic foreign key
    """
    def __init__(self, expr, owner_name):
        self.owner = owner_name
        super(SlaveComparator, self).__init__(expr)

    def __eq__(self, other):
        self.__clause_element__().append_whereclause(
                "{}_id = {}".format(self.owner, other.id))

        return db.exists(self.__clause_element__())


def generic_owner_for(*args):
    """Creates an association_table and relation attribute,
       called "association" and adds generic foreign key property,
       called "owner", for generic owners from args
    """
    for cls in args:
        cls_name = cls.__name__
        association_name = "{}Association".format(cls_name)
        column_name = cls_name.lower()
        association_table = "{}_association".format(column_name)
        if db.metadata.tables.get(association_table) is not None:
            return cls

        attrs = {"{}_id".format(column_name): db.Column(db.Integer,
                        db.ForeignKey("{}.id".format(cls.__tablename__),
                                      ondelete='CASCADE'),
                        primary_key=True),
                 'owner_id': db.Column(db.Integer, primary_key=True),
                 'owner_table': db.Column(db.String(128))}
        cls_association = type(association_name, (db.Model, BaseMixin), attrs)

        setattr(cls, 'association', db.relationship(association_name,
                primaryjoin="{}.id=={}.{}_id".format(cls_name,
                                                     association_name,
                                                     column_name),
                backref="{}".format(column_name), uselist=False,
                        cascade="all, delete-orphan"))

        def getter(self):
            owner_table = self.association.owner_table
            if owner_table is None:
                return None

            subquery = db.select(["*"],
                "id = {:d}".format(self.association.owner_id), owner_table)

            return dict_obj(db.engine.execute(subquery).first())

        def setter(self, value):
            self.association = cls_association(owner_id=value.id,
                                               owner_table=value.__tablename__)

        def comparator(cls):
            return GenericOwnerComparator(cls.association)

        owner = hybrid_property(getter, setter)
        setattr(cls, 'owner', owner.comparator(comparator))

        return cls


def owner_wrapper(slave_cls, cls):
    """Creates relation for a slave that
       is generic foreign key owner
    """
    slave_table = slave_cls.__tablename__
    slave_cls_name = slave_cls.__name__.lower()
    table_name = "{}_association".format(slave_cls.__name__.lower())
    association_table = db.metadata.tables.get(table_name)

    def getter(self):
        whereclause = "owner_id={} and owner_table='{}'".format(self.id,
                                                         self.__tablename__)
        subquery = slave_cls.query.join(slave_cls.association). \
                        with_transformation(filter_wrapper(whereclause))
        return subquery

    def setter(self, value):
        db.engine.execute(association_table.insert(),
                          {"{}_id".format(slave_cls_name): value.id,
                           'owner_id': self.id,
                           'owner_table': self.__tablename__})

    def deleter(self):
        for owned in getter(self).all():
            owned.delete()

    def expression(self):
        subquery = db.select(['1'],
                             "owner_id = users.id AND owner_table = '{table}'".
                             format(table=cls.__tablename__),
                             table_name)
        return subquery

    def comparator(self):
        return SlaveComparator(expression(self), slave_cls_name)

    slave = hybrid_property(getter, setter, deleter)
    setattr(cls, "owned_{}".format(slave_table), slave.comparator(comparator))

    return cls

album_owner = lambda cls: owner_wrapper(Album, cls)
generic_owner_for(Album)
