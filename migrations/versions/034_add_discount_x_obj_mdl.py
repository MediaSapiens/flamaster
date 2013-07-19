from sqlalchemy import *
from migrate import *

meta = MetaData()
discount_x_object = Table('discount_x_object', meta,
                  Column('id', Integer, primary_key=True),
                  Column('discount_id', Integer),
                  Column('object_id', Integer)
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    discount_x_object.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    discount_x_object.drop()
