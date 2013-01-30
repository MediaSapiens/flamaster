from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    state = Column('state', Integer(), default=0)
    state.create(orders)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    orders.c.state.drop()
