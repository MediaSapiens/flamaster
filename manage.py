#!/usr/bin/env python

from flamaster.app import db, init_all
from flask.ext.script import Manager
from flamaster.core.commands import CreateAll, DropAll

manager = Manager(init_all(db))


if __name__ == '__main__':
    manager.add_command('createall', CreateAll())
    manager.add_command('dropall', DropAll())
    manager.run()
