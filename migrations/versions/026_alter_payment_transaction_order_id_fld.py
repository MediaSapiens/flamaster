from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    payment_transactions = Table('payment_transactions', meta, autoload=True)
    payment_transactions.c.order_id.alter(nullable=True)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    payment_transactions = Table('payment_transactions', meta, autoload=True)
    payment_transactions.c.order_id.alter(nullable=False)
