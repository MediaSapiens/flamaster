from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    cart = Table('carts', meta, autoload=True)
    discount_unit_price = Column('discount_unit_price', Numeric(precision=18, scale=2))
    discount_net_price = Column('discount_net_price', Numeric(precision=18, scale=2))
    discount_price = Column('discount_price', Numeric(precision=18, scale=2))
    discount_unit_price.create(cart)
    discount_net_price.create(cart)
    discount_price.create(cart)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    cart = Table('carts', meta, autoload=True)
    cart.c.discount_unit_price.drop()
    cart.c.discount_net_price.drop()
    cart.c.discount_price.drop()
