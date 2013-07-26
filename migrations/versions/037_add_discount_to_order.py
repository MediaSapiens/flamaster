from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    order = Table('orders', meta, autoload=True)
    total_discount = Column('total_discount', Numeric(precision=18, scale=2))
    delivery_free = Column('delivery_free', Boolean, default=False)
    total_discount.create(order)
    delivery_free.create(order)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    order = Table('orders', meta, autoload=True)
    order.c.total_discount.drop()
    order.c.delivery_free.drop()
