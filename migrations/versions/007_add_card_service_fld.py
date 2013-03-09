from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    cart = Table('carts', meta, autoload=True)
    service = Column('service', String(), default='')
    service.create(cart)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    cart = Table('carts', meta, autoload=True)
    cart.c.service.drop()
