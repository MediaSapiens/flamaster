#!/usr/bin/env python

from flamaster.app import app_ready
from flask.ext.script import Manager


manager = Manager(app_ready)

if __name__ == '__main__':
    manager.run()
