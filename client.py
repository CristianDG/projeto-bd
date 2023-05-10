import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from API import app, db

class TestAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:teste123@projetobd-aws-caju.cgsu9rzobayk.us-east-1.rds.amazonaws.com:5432/projeto_bd_caju"
        self.app = app.test_client()

        with app.app_context():  # Criando o contexto de aplicação
            db.create_all()
    
    def tearDown(self):
        with app.app_context():  # Criando o contexto de aplicação
            db.session.remove()
            db.drop_all()
    
    def test_criar_usuario(self):
        response = self.app.post('/usuarios', json={'nome':'Arthur Henrique', 'senha': 'teste123', 'permissao_moderador':True, 'id_associacao_criticos': None})
        self.assertEqual(response.status_code, 201)
    
if __name__ == '__main__':
    unittest.main()
