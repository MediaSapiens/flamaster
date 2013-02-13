from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    notes = Column('notes', UnicodeText(), default=u'')
    notes.create(orders)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    orders.c.notes.drop()
