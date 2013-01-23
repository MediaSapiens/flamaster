from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    shop_id = Column('shop_id', String(128), default='1')
    shop_id.create(orders)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    orders.c.shop_id.drop()
