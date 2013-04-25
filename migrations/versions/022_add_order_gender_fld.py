from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)

    billing_gender = Column('billing_gender', Unicode(255), default=u'')
    delivery_gender = Column('delivery_gender', Unicode(255), default=u'')

    billing_gender.create(orders)
    delivery_gender.create(orders)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)

    orders.c.billing_gender.drop()
    orders.c.delivery_gender.drop()
