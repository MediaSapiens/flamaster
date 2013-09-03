from sqlalchemy import *
from migrate import *
from sqlalchemy.dialects import postgresql


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    category = Table('categories', meta, autoload=True)
    shops = Column('shops', postgresql.ARRAY(Integer))
    shops.create(category)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    category = Table('categories', meta, autoload=True)
    category.c.shops.drop()
