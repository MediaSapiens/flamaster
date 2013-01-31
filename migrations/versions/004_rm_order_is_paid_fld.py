from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    orders.c.is_paid.drop()


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    is_paid = Column('is_paid', Boolean(), default=True)
    is_paid.create(orders)
