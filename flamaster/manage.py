#!/usr/bin/env python
from app import app
from flaskext.script import Manager

manager = Manager(app)


if __name__ == '__main__':
    manager.run()
