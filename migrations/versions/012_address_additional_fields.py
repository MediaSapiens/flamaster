from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    address = Table('addresses', meta, autoload=True)
    first_name = Column('first_name', Unicode(255), default=u'')
    last_name = Column('last_name', Unicode(255), default=u'')
    company = Column('company', Unicode(255), default=u'')
    first_name.create(address)
    last_name.create(address)
    company.create(address)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    address = Table('addresses', meta, autoload=True)
    address.c.first_name.drop()
    address.c.last_name.drop()
    address.c.company.drop()
