from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    enums = ['user', 'product', 'category', 'cart']
    change_type(enums, migrate_engine)


def downgrade(migrate_engine):
    enums = ['user', 'product', 'category']
    change_type(enums, migrate_engine)


def change_type(enums=[], migrate_engine=None):
    meta = MetaData(bind=migrate_engine)
    discounts = Table('discounts', meta, autoload=True)

    # Select data
    data = migrate_engine.execute(discounts.select()).fetchall()

    # Delete all the data in order to remove the field
    migrate_engine.execute("DELETE FROM discounts")

    discounts = Table('discounts', meta, autoload=True)

    # Drop field and type
    discounts.c.group_type.drop()
    Enum(metadata=meta, name="group_type").drop()

    # Create type and field
    new_type = Enum(*enums, metadata=meta, name="group_type")
    new_type.create()

    group_type = Column('group_type', new_type, nullable=False)
    group_type.create(discounts)

    # Insert data
    data = filter(lambda row: row['group_type'] in enums, data)
    if data:
        migrate_engine.execute(discounts.insert(), data)
