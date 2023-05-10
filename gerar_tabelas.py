#!/usr/bin/env python3

from src.API import app, db

with app.app_context():
    db.drop_all()
    db.create_all()
