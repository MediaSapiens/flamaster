from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    categories = Table('categories', meta, autoload=True)
    image = Column('image', String(255), default='')
    image.create(categories)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    categories = Table('categories', meta, autoload=True)
    categories.c.image.drop()
