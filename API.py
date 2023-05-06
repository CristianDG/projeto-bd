from typing import Any
from sqlalchemy import create_engine, Column, Integer, String

from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

from flask import Flask, jsonify, request


url_banco = ""
engine = create_engine(url_banco)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Pesquisar como se faz a referência de chave estrangeira com orm

# Criar Classes para todas as entidades.

class Usuario(Base):
    id = Column(String, primary_key="True")
    nome = Column(String)
    senha = Column(String)
    # permissao_moderador = Column() Booleano]
    # id_associacao_criticos = Column(Integer)

    def __init__(self, nome, senha, permissao, id_associacao):
        self.nome = nome
        self.senha = senha
        self.permissao_moderador = permissao
        self.id_associacao_criticos = id_associacao


class Associacao_Criticos(Base):
    id = Column(Integer, primary_key="True")
    nome = Column(String)

    def __init__(self):
        print("to do")


class Critica(Base):
    id = Column(Integer, primary_key="True")
    conteudo = Column(String)
    # nota = Column(Float)
    # data = Column(date)
    # id_usuario = Column(String)

    def __init__(self):
        print("to do")
    

class Criticas_Obras(Base):
    id_obra = Column(Integer)
    id_critica = Column(Integer)

    def __init__(self):
        print("to do")

class Obra(Base):
    id = Column(Integer, primary_key="True")
    nome = Column(String)
    id_produtora = Column(Integer)
    genero = Column(String)
    sinopse = Column(String)
    # data_estreia = Column(date)
    # relacionados = Columnn(json)

    def __init__(self):
        print("to do")


class Genero(Base):
    id = Column(String, primary_key="True")

    def __init__(self):
        print("to do")


class Filme(Base):
    id = Column(Integer)
    bilheteria = Column(Integer)

    def __init__(self):
        print("to do")
    

class Serie(Base):
    id = Column(Integer, primary_key="True")
    # data_fim = Column(date)
    episodios = Column(Integer)


    def __init__(self):
        print("to do")

class Produtora(Base):
    id = Column(Integer, primary_key="True")
    nome = Column(String)

    def __init__(self):
        print("to do")

class Premio(Base):
    id = Column(Integer, primary_key="True")
    nome = Column(String)
    categoria = Column(String)
    # data = Column(date)


    def __init__(self):
        print("to do")


class Staff(Base):
    id = Column(Integer, primary_key="True")
    nome_artístico = Column(String)
    nome = Column(String)
    # data_nascimento = Columnd(Date)

    # foto = Column()

    local_nascimento = Column(String)
    # maior_nota_recebida = Column(Float)
    # menor_nota_recebida = Column(FLoat)

    def __init__(self):
        print("to do")
    

class Cargo(Base):
    id = Column(String, primary_key="True")

    def __init__(self):
        print("to do")


app = Flask(__name__)