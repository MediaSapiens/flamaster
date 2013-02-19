from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    categories = Table('categories', meta, autoload=True)
    is_deleted = Column('is_deleted', Boolean(), default=False)
    is_visible = Column('is_visible', Boolean(), default=True)
    is_deleted.create(categories)
    is_visible.create(categories)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    categories = Table('categories', meta, autoload=True)
    categories.c.is_deleted.drop()
    categories.c.is_visible.drop()
