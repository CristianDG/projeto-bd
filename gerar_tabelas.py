#!/usr/bin/env python3

from src.API import app, db, Usuario, criptografar

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.add(Usuario(
        nome="adm",
        senha=criptografar("adm"),
        permissao_mod=True,
        id_associacao_criticos=None
    ))

    db.session.commit()
