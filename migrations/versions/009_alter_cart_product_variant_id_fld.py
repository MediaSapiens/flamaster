from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    cart = Table('carts', meta, autoload=True)
    cart.c.product_variant_id.alter(nullable=True)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    cart = Table('carts', meta, autoload=True)
    cart.c.product_variant_id.alter(nullable=False)
