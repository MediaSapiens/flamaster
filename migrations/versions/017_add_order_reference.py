from sqlalchemy import *
from migrate import *
from migrate.changeset.constraint import UniqueConstraint


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    reference = Column('reference', String(16))
    reference.create(orders)
    UniqueConstraint(reference).create()


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    orders.c.reference.drop()
