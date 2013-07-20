from sqlalchemy import *
from migrate import *
from datetime import datetime

meta = MetaData()
discount_x_object = Table('discount_x__users', meta,
                  Column('id', Integer, primary_key=True),
                  Column('discount_id', Integer),
                  Column('user_id', Integer),
                  Column('created_at', DateTime, default=datetime.utcnow())
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    discount_x_object.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    discount_x_object.drop()
