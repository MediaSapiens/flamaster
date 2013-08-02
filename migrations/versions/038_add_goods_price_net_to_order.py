from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    order = Table('orders', meta, autoload=True)
    goods_price_net = Column('goods_price_net', Numeric(precision=18, scale=2))
    goods_price_net.create(order)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    order = Table('orders', meta, autoload=True)
    order.c.goods_price_net.drop()
