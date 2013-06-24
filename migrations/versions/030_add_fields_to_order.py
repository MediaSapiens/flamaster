from sqlalchemy import *
from migrate import *
from settings import PAYMENT_VAT, DELIVERY_VAT
def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    order = Table('orders', meta, autoload=True)
    payment_vat = Column('payment_vat', Numeric(precision=18, scale=2), default=PAYMENT_VAT)
    delivery_vat = Column('delivery_vat', Numeric(precision=18, scale=2), default = DELIVERY_VAT)
    payment_vat.create(order)
    delivery_vat.create(order)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    order = Table('orders', meta, autoload=True)
    order.c.payment_vat.drop()
    order.c.delivery_vat.drop()