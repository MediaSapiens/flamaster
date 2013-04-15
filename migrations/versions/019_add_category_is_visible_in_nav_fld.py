from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    categories = Table('categories', meta, autoload=True)
    is_visible_in_nav = Column('is_visible_in_nav', Boolean, default=True)
    is_visible_in_nav.create(categories)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    categories = Table('categories', meta, autoload=True)
    categories.c.is_visible_in_nav.drop()
