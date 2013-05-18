from sqlalchemy import *
from migrate import *
from migrate.changeset.constraint import UniqueConstraint


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    payment_fee = Column('payment_fee', Numeric(precision=18, scale=2))
    payment_fee.create(orders)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    orders.c.payment_fee.drop()
