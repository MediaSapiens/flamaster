#!/usr/bin/env python
from migrate.versioning.shell import main

import os
import sys


dir = os.path.dirname
sys.path.insert(0, dir(dir(dir(os.path.abspath(__file__)))))

import settings


if __name__ == '__main__':
    main(url=settings.SQLALCHEMY_DATABASE_URI,
         debug='False',
         repository=settings.MIGRATIONS_REPOSITORY)