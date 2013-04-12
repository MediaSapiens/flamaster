from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    customers = Table('customers', meta, autoload=True)
    birth_date = Column('birth_date', Date)
    birth_date.create(customers)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    customers = Table('customers', meta, autoload=True)
    customers.c.birth_date.drop()
