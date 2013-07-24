from sqlalchemy import *
from migrate import *
from datetime import datetime



meta = MetaData()
discounts = Table('discounts', meta,
              Column('id', Integer, primary_key=True),
              Column('group_name', Unicode(255)),
              Column('discount', Integer, nullable=False),
              Column('group_type', Enum('user', 'product', 'category', 'cart', name="group_type"), nullable=False),
              Column('created_at', DateTime, default=datetime.utcnow())
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    discounts.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    discounts.drop()
