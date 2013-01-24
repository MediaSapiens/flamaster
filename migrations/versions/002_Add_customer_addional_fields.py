from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    customers = Table('customers', meta, autoload=True)
    fax = Column('fax', String(80), default='')
    gender = Column('gender', String(1), default='')
    company = Column('company', Unicode(255), default=u'')
    fax.create(customers)
    gender.create(customers)
    company.create(customers)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    customers = Table('customers', meta, autoload=True)
    customers.c.fax.drop()
    customers.c.gender.drop()
    customers.c.company.drop()
