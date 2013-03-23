from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    categories = Table('categories', meta, autoload=True)
    slug = Column('_slug', Unicode(128), default=u'')
    categories.c.name.alter(Unicode(512))
    slug.create(categories)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    categories = Table('categories', meta, autoload=True)
    categories.c.name.alter(Unicode(256))
    categories.c._slug.drop()
