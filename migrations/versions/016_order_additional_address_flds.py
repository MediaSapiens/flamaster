from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)
    billing_first_name = Column('billing_first_name', Unicode(255), default=u'')
    billing_last_name = Column('billing_last_name', Unicode(255), default=u'')
    billing_company = Column('billing_company', Unicode(255), default=u'')
    billing_phone = Column('billing_phone', String(17), default='')

    delivery_first_name = Column('delivery_first_name', Unicode(255), default=u'')
    delivery_last_name = Column('delivery_last_name', Unicode(255), default=u'')
    delivery_company = Column('delivery_company', Unicode(255), default=u'')
    delivery_phone = Column('delivery_phone', String(17), default='')

    billing_first_name.create(orders)
    billing_last_name.create(orders)
    billing_company.create(orders)
    billing_phone.create(orders)

    delivery_first_name.create(orders)
    delivery_last_name.create(orders)
    delivery_company.create(orders)
    delivery_phone.create(orders)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    orders = Table('orders', meta, autoload=True)

    orders.c.billing_first_name.drop()
    orders.c.billing_last_name.drop()
    orders.c.billing_company.drop()
    orders.c.billing_phone.drop()

    orders.c.delivery_first_name.drop()
    orders.c.delivery_last_name.drop()
    orders.c.delivery_company.drop()
    orders.c.delivery_phone.drop()
