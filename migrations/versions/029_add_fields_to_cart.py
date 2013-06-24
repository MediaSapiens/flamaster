from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    cart = Table('carts', meta, autoload=True)
    unit_price = Column('unit_price', Numeric(precision=18, scale=2))
    vat = Column('vat', Numeric(precision=18, scale=2))
    unit_price.create(cart)
    vat.create(cart)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    cart = Table('carts', meta, autoload=True)
    cart.c.unit_price.drop()
    cart.c.vat.drop()

