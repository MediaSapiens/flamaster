from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    customers = Table('customers', meta, autoload=True)
    customers.c.direct_debit.drop()
    customers.c.swift.drop()
    customers.c.account_number.drop()
    customers.c.blz.drop()

    users = Table('users', meta, autoload=True)

    direct_debit = Column('direct_debit', Boolean, default=False)
    swift = Column('swift', String(80), default='')
    account_number = Column('account_number', String(80), default='')
    blz = Column('blz', String(80), default='')
    iban = Column('iban', String(80), default='')

    direct_debit.create(users)
    swift.create(users)
    account_number.create(users)
    blz.create(users)
    iban.create(users)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    users = Table('users', meta, autoload=True)
    users.c.direct_debit.drop()
    users.c.swift.drop()
    users.c.account_number.drop()
    users.c.blz.drop()
    users.c.iban.drop()

    customers = Table('customers', meta, autoload=True)

    direct_debit = Column('direct_debit', Boolean, default=False)
    swift = Column('swift', String(80), default='')
    account_number = Column('account_number', String(80), default='')
    blz = Column('blz', String(80), default='')

    direct_debit.create(customers)
    swift.create(customers)
    account_number.create(customers)
    blz.create(customers)
