from sqlalchemy import *
from migrate import *
from datetime import datetime
from flamaster.conf.settings import BABEL_DEFAULT_LOCALE as lang

meta = MetaData()

def get_table(migrate_engine):
    meta.bind = migrate_engine

    flat_pages = Table('flat_pages', meta, autoload=True)

    flat_page_localizeds = Table('flat_page_localizeds', meta,
                  Column('id', Integer, primary_key=True),
                  Column('name', Unicode(512), nullable=False),
                  Column('content', UnicodeText),
                  Column('template_name', Unicode(512)),
                  Column('parent_id', Integer, ForeignKey('flat_pages.id',
                                                        ondelete="CASCADE",
                                                        onupdate="CASCADE")),
                  Column('locale', Unicode(255), default=unicode(lang), index=True),
                  Column('created_at', DateTime, default=datetime.utcnow())
    )

    return flat_page_localizeds


def upgrade(migrate_engine):
    flat_page_localizeds = get_table(migrate_engine)
    flat_page_localizeds.create()


def downgrade(migrate_engine):
    flat_page_localizeds = get_table(migrate_engine)
    flat_page_localizeds.drop()
