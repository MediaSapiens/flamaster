#!/usr/bin/env python

from flamaster.app import app_ready
from flask.ext.script import Manager
from flamaster.core.commands import CreateAll

manager = Manager(app_ready)


if __name__ == '__main__':
#    manager.add_command('createall', CreateAll())
    manager.run()
