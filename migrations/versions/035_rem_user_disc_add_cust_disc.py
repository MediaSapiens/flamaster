from sqlalchemy import *
from migrate import *
from datetime import datetime


meta = MetaData()
discount_x_user = Table('discount_x__users', meta,
                          Column('id', Integer, primary_key=True),
                          Column('discount_id', Integer, ForeignKey("discounts.id")),
                          Column('user_id', Integer, ForeignKey("customers.id")),
                          Column('created_at', DateTime, default=datetime.utcnow())
)


discount_x_customer = Table('discount_x__customers', meta,
                          Column('id', Integer, primary_key=True),
                          Column('discount_id', Integer, ForeignKey("discounts.id")),
                          Column('customer_id', Integer, ForeignKey("customers.id")),
                          Column('created_at', DateTime, default=datetime.utcnow())
)



def upgrade(migrate_engine):
    meta.bind = migrate_engine
    customers = Table('customers', meta, autoload=True)
    discounts = Table('discounts', meta, autoload=True)
    discount_x_user.drop()
    discount_x_customer.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    customers = Table('customers', meta, autoload=True)
    discounts = Table('discounts', meta, autoload=True)
    discount_x_user.create()
    discount_x_customer.drop()

