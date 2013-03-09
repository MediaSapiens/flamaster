from migrate.changeset.constraint import UniqueConstraint
from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    shelfs = Table('shelfs', meta, autoload=True)
    product_id = Column('product_id', String(), nullable=False)
    product_id.create(shelfs)
    Index('ix_shelfs_product_id', shelfs.c.product_id).create()
    UniqueConstraint('product_id', table=shelfs).create()


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    shelfs = Table('shelfs', meta, autoload=True)
    UniqueConstraint('product_id', table=shelfs).drop()
    Index('ix_shelfs_product_id', shelfs.c.product_id).drop()
    shelfs.c.product_id.drop()