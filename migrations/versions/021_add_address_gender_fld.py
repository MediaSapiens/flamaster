from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    addresses = Table('addresses', meta, autoload=True)
    gender = Column('gender', String(1), default='')
    gender.create(addresses)
    pass


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    addresses = Table('gender', meta, autoload=True)
    addresses.c.gender.drop()
