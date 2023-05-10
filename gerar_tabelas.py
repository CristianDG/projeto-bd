#!/usr/bin/env python3

from src.API import app, db

with app.app_context():
    db.create_all()
