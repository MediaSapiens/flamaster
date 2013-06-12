from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    categories = Table('categories', meta, autoload=True)
    shop_id = Column('shop_id', Integer())
    show_on_homepage = Column('show_on_homepage', Boolean(), default=False)
    shop_id.create(categories)
    show_on_homepage.create(categories)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    categories = Table('categories', meta, autoload=True)
    categories.c.shop_id.drop()
    categories.c.show_on_homepage.drop()
