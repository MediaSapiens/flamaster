from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    flat_page_localizeds = Table('flat_page_localizeds', meta, autoload=True)
    flat_page_localizeds.c.name.alter(default='')
    flat_page_localizeds.c.template_name.alter(default='')
    flat_page_localizeds.c.content.alter(default='')


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    flat_page_localizeds = Table('flat_page_localizeds', meta, autoload=True)
    flat_page_localizeds.c.name.alter(default=None)
    flat_page_localizeds.c.template_name.alter(default=None)
    flat_page_localizeds.c.content.alter(default=None)
