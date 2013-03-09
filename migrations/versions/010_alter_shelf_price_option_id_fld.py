from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    shelfs = Table('shelfs', meta, autoload=True)
    shelfs.c.price_option_id.alter(name='product_variant_id')


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    shelfs = Table('shelfs', meta, autoload=True)
    shelfs.c.product_variant_id.alter(name='price_option_id')
