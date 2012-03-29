#!/usr/bin/env python

from flamaster.app import app
from flask.ext.script import Manager
from flamaster.core.commands import CreateAll, DropAll

manager = Manager(app)


if __name__ == '__main__':
    manager.add_command('createall', CreateAll())
    manager.add_command('dropall', DropAll())
    manager.run()
