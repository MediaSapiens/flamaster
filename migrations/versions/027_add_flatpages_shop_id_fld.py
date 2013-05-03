from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    flatpages = Table('flat_pages', meta, autoload=True)
    shop_id = Column('shop_id', String(128), default='1')
    shop_id.create(flatpages)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    flatpages = Table('flat_pages', meta, autoload=True)
    flatpages.c.shop_id.drop()