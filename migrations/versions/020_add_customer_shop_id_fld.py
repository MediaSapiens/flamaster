from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    customers = Table('customers', meta, autoload=True)
    shop_id = Column('shop_id', String(128), default='1')
    shop_id.create(customers)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    customers = Table('customers', meta, autoload=True)
    customers.c.shop_id.drop()