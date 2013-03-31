from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    addresses = Table('addresses', meta, autoload=True)
    phone = Column('phone', String(17), default='')
    phone.create(addresses)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    addresses = Table('addresses', meta, autoload=True)
    addresses.c.phone.drop()
