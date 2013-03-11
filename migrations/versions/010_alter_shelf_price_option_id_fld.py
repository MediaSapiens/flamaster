from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    shelfs = Table('shelfs', meta, autoload=True)
    shelfs.c.price_option_id.alter(name='product_variant_id')
    #Index('ix_shelfs_price_option_id', shelfs.c.product_id).drop()


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    shelfs = Table('shelfs', meta, autoload=True)
    shelfs.c.product_variant_id.alter(name='price_option_id')
    #Index('ix_shelfs_price_option_id', shelfs.c.product_id, unique=True).create()
