#!/usr/bin/env python

from flamaster.app import app, assets
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from flamaster.core.commands import CreateAll, DropAll


manager = Manager(app)


if __name__ == '__main__':
    manager.add_command('createall', CreateAll())
    manager.add_command('dropall', DropAll())
    manager.add_command("assets", ManageAssets(assets))
    manager.run()
