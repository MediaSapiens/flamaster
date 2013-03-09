from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    carts = Table('carts', meta, autoload=True)
    carts.c.price_option_id.drop()


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    carts = Table('carts', meta, autoload=True)
    price_option_id = Column('price_option_id', String(), nullable=False)
    price_option_id.create(carts)
