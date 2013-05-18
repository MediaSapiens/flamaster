from sqlalchemy import *
from migrate import *

from datetime import datetime


meta = MetaData()
payment_transactions = Table(
    'payment_transactions', meta,
    Column('id', Integer, primary_key=True),
    Column('status', Integer, index=True, nullable=False),
    Column('details', UnicodeText, unique=True, nullable=False),
    Column('order_id', Integer, ForeignKey('orders.id'), nullable=False, index=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    orders = Table('orders', meta, autoload=True)
    payment_transactions.create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    payment_transactions.drop()