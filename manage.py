#!/usr/bin/env python
# encoding: utf-8

from auth import create_app
from auth.models import db
from auth.services import manager

import auth.commands

if __name__ == '__main__':
    app = create_app()
    db.init_app(app)
    manager.app = app
    manager.run()
