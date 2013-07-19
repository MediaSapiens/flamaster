from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    discounts = Table('discounts', meta, autoload=True)
    date_from = Column('date_from', Date)
    date_to = Column('date_to', Date)
    free_delivery = Column('free_delivery', Boolean, default=False)
    min_value = Column("min_value", Numeric(precision=18, scale=2))
    date_from.create(discounts)
    date_to.create(discounts)
    free_delivery.create(discounts)
    min_value.create(discounts)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    discounts = Table('discounts', meta, autoload=True)
    discounts.c.date_from.drop()
    discounts.c.date_to.drop()
    discounts.c.free_delivery.drop()
    discounts.c.min_value.drop()