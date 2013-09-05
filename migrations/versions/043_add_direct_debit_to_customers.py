from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    customers = Table('customers', meta, autoload=True)

    direct_debit = Column('direct_debit', Boolean, default=False)
    swift = Column('swift', String(80), default='')
    account_number = Column('account_number', String(80), default='')
    blz = Column('blz', String(80), default='')

    direct_debit.create(customers)
    swift.create(customers)
    account_number.create(customers)
    blz.create(customers)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    cart = Table('customers', meta, autoload=True)

    cart.c.direct_debit.drop()
    cart.c.swift.drop()
    cart.c.account_number.drop()
    cart.c.blz.drop()
