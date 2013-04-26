from sqlalchemy import *
from migrate import *

from migrate.changeset.constraint import UniqueConstraint


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    flatpages = Table('flat_pages', meta, autoload=True)
    slug = Column('slug', String(256), nullable=False)
    flatpages.c._slug.drop()
    slug.create(flatpages)
    UniqueConstraint(slug).create()


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    flatpages = Table('flat_pages', meta, autoload=True)
    _slug = Column('_slug', String(128), nullable=False, unique=True)
    flatpages.c.slug.drop()
    _slug.create(flatpages)
    UniqueConstraint(_slug).create()
