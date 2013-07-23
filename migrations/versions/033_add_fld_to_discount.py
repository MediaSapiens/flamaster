from sqlalchemy import *
from migrate import *

discount_t = Enum('percent', 'currency',  name="discount_type")

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)

    shops = Table('shops', meta, autoload=True)
    discounts = Table('discounts', meta, autoload=True)

    date_from = Column('date_from', Date)
    date_to = Column('date_to', Date)
    free_delivery = Column('free_delivery', Boolean, default=False)
    min_value = Column("min_value", Numeric(precision=18, scale=2))
    shop_id = Column("shop_id", Integer, ForeignKey('shops.id'))
    discount_type = Column('discount_type', discount_t,  nullable=False)
    amount = Column('amount', Numeric(precision=18, scale=2))

    discount_t.create(bind=migrate_engine)
    discount_type.create(discounts)
    date_from.create(discounts)
    date_to.create(discounts)
    free_delivery.create(discounts)
    min_value.create(discounts)
    shop_id.create(discounts)

    amount.create(discounts)

    discounts.c.discount.drop()


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    discounts = Table('discounts', meta, autoload=True)

    discounts.c.date_from.drop()
    discounts.c.date_to.drop()
    discounts.c.free_delivery.drop()
    discounts.c.min_value.drop()
    discounts.c.shop_id.drop()
    discounts.c.discount_type.drop()
    discounts.c.amount.drop()

    discount = Column('discount', Integer, nullable=False)

    discount.create(discounts)
    discount_t.drop(bind=migrate_engine)
