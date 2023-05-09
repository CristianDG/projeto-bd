from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date
from sqlalchemy_utils import JSONType

import jwt
import os
from datetime import datetime as dt, timedelta
from functools import wraps
from hashlib import sha256





app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:teste123@projetobd-aws-caju.cgsu9rzobayk.us-east-1.rds.amazonaws.com:5432/projeto_bd_caju"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Criar Classes para todas as entidades.
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String())
    senha = db.Column(db.String())
    permissao_moderador = db.Column(db.Boolean)
    ultimo_acesso = db.Column(Date)
    id_associacao_criticos = db.Column(db.Integer, db.ForeignKey('Associacao_Criticos.id'))


    def __init__(self, nome, senha, permissao_mod, ult_acesso, id_associacao_crit):
        self.nome = nome
        self.senha = senha
        self.permissao_moderador = permissao_mod
        self.ultimo_acesso = ult_acesso
        self.id_associacao_criticos = id_associacao_crit

class Associacao_Criticos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String())

    def __init__(self, nome):
        self.nome = nome



class Critica(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conteudo = db.Column(db.String())
    nota = db.Column(db.Float)
    data = db.Column(Date)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id'))

    def __init__(self, conteudo, nota, data, id_usuario):
        self.conteudo = conteudo
        self.nota = nota
        self.data = data
        self.id_usuario = id_usuario

class Obra(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String())
    id_produtora = db.Column(db.Integer, db.ForeignKey('Produtora.id'))
    genero = db.Column(db.String, db.ForeignKey('Genero.id'), nullable=False)
    sinopse = db.Column(db.String())
    tipo = db.Column(db.String(1))
    data_estreia = db.Column(Date)
    filmes = db.relationship('Filme', backref='Obra', cascade='all, delete')
    series = db.relationship('Serie', backref='Obra', cascade='all, delete')

    def __init__(self, nome, id_prod, genero, sinopse, data_estreia, relacionados):
        self.nome = nome
        self.id_produtora = id_prod
        self.genero = genero
        self.sinopse = sinopse
        self.data_estreia = data_estreia
    

class Criticas_Obras(db.Model):
    id_obra = db.Column(db.Integer, db.ForeignKey('Obra.id'), primary_key = True)
    id_critica = db.Column( db.Integer, db.ForeignKey('Critica.id'), primary_key=True)

    def __init__(self):
        pass


class Genero(db.Model):
    id = db.Column(db.String(), primary_key=True)
    def __init__(self):
        pass

class Filme(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('Obra.id'), primary_key=True)
    bilheteria = db.Column(db.Integer)
    
    def __init__(self, bilheteria):
        self.bilheteria = bilheteria

class Serie(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('Obra.id'), primary_key=True)
    data_fim = db.Column(Date)
    episodios = db.Column(db.Integer)

    def __init__(self, data, ep):
        self.data_fim = data
        self.episodios = ep

class Produtora(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String())

    def __init__(self, nome):
        self.nome = nome


class Premio(db.Model):
    id = db.Column(db.Integer, primary_key="True", autoincrement=True)
    nome = db.Column(db.String)
    categoria = db.Column(db.String())
    data = db.Column(Date)


    def __init__(self, nome, categ, data):
        self.nome = nome
        self.categoria = categ
        self.data = data



class Staff(db.Model):
    id = db.Column(db.Integer, primary_key="True", autoincrement=True)
    nome_artístico = db.Column(db.String())
    nome = db.Column(db.String())
    data_nascimento = db.Column(Date)
    foto = db.Column(db.LargeBinary())
    local_nascimento = db.Column(db.String())

    def __init__(self, nome, nome_art, data_nasc, foto, local_nasc):
        self.nome = nome
        self.nome_artístico = nome_art
        self.data_nascimento = data_nasc
        self.foto = foto
        self.local_nascimento = local_nasc
    

class Cargo(db.Model):
    id = db.Column(db.String(), primary_key="True")

    def __init__(self):
        pass

def encode(dados):
    return jwt.encode(dados, os.getenv('JWT_SECRET'), algorithm='HS256')

def decode(dados):
    return jwt.decode(dados, os.getenv('JWT_SECRET'), algorithms=["HS256"])

def criptografar(senha):
    return sha256(bytes(senha ,'utf8')).hexdigest()

def autenticar(usuario=False, moderador=False):

    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            erro = { 'error': 'não autorizado' }, 401

            if 'Authorization' not in request.headers:
                return erro

            token = decode(request.headers['Authorization'])
            id_usuario = None
            try:
                id_usuario = int(token['id'])
            except:
                return erro

            ttl_token = timedelta(hours=3)

            data_token = dt.fromtimestamp(token['data'])
            agora = dt.now()

            # TODO: controlar a data do token com a data do último acesso
            if (agora - data_token) > ttl_token:
                return {'error': 'token expirado'}, 403


            # TODO: pegar o usuario pelo id
            #usuario = UsuarioController.procurar_por_id(id_usuario)
            user = None
            if not user:
                return erro


            # FIXME mudar
            if (moderador and not user.admin) and (moderador and user.admin):
                return erro

            return fn(*args, **kwargs, usuario_solicitante=usuario)

        return inner
    return wrapper

@app.post('/login')
def login():
    usuario_json = request.get_json()

    # TODO: pegar o usuario do banco
    #usuario = UsuarioController.procurar_por_login(usuario_json['email'], criptografar(usuario_json['senha']))
    usuario = None
    if not usuario:
        return {'error': 'email ou senha incorretos'}, 400

    # TODO: mudar o ultimo acesso e retornar no lugar da data de agora
    token = encode({'id': usuario.id, 'data': dt.now().timestamp()})

    return { 'token': token, 'adm': usuario.admin }, 200

# Rotas
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify(
        [{
            'id':usuario.id,
            'nome':usuario.nome,
            'permissão_moderador':usuario.permissao_moderador,
            'associação_criticos':usuario.id_associacao_criticos
        }for usuario in usuarios]
    )

@app.route('/usuarios', methods=['POST'])
def cadastrar_usuario():
    user = Usuario(request.json['nome', request.json['senha'], request.json['permissao_moderador'], request.json['id_associacao_criticos']])
    db.session.add(user)
    db.session.commit()
    return jsonify(
        [{
            'id':user.id,
            'nome':user.nome,
            'permissão_moderador':user.permissao_moderador,
            'associação_criticos':user.id_associacao_criticos
        }]
    )


@app.route('/usuarios/<int:usuario_id>', methods=['GET'])
def buscar_usuario(usuario_id):
    user = Usuario.query.get(usuario_id)
    if user:
        return jsonify(
            [{
                'id':user.id,
                'nome':user.nome,
                'permissão_moderador':user.permissao_moderador,
                'associação_criticos':user.id_associacao_criticos
            }]
        )
    else:
        return jsonify({'mensagem':'Usuario não encontrado.'}), 404


@app.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def atualizar_usuario(usuario_id):
    user = Usuario.query.get(usuario_id)
    if user:
        user.nome = request.json.get('nome', user.nome)
        db.session.commit()
        return jsonify(
            [{
                'id':user.id,
                'nome':user.nome,
                'permissão_moderador':user.permissao_moderador,
                'associação_criticos':user.id_associacao_criticos
            }]
        )
    else:
        return jsonify({'mensagem':'Usuario não encontrado.'}), 404


@app.route('/usuarios/<int:usuario_id_mod>/<int:usuario_id>', methods=['DELETE'])
def excluir_usuario(usuario_id_mod, usuario_id):
    user_mod = Usuario.query.get(usuario_id_mod)
    if user_mod.permissao_moderador == True:
        user = Usuario.query.get(usuario_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return '', 204
        else:
            return jsonify({'mensagem':'Usuario não encontrado.'}), 404
    elif user_mod.permissao_moderador == False:
        return jsonify({'mensagem':'Usuário não possui permissão para moderação.'}), 403
    else:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404



@app.route('/associacao_criticos', methods=['GET'])
def listar_assoc_criticos():
    assoc_crits = Associacao_Criticos.query.all()
    return jsonify(
        [{
            'id': assoc_crits.id,
            'nome': assoc_crits.nome
        }]
    )

@app.route('/associacao_criticos', methods=['POST'])
def cadastrar_assoc_criticos():
    assoc_crit = Associacao_Criticos(request.json['nome'])
    db.session.add(assoc_crit)
    db.session.commit()
    return jsonify(
        [{
            'id': assoc_crit.id,
            'nome': assoc_crit.nome
        }]
    )


@app.route('/associacao_criticos/<int:assoc_crit_id>', methods=['GET'])
def buscar_assoc_crit(assoc_crit_id):
    assoc_crit = Associacao_Criticos.query.get(assoc_crit_id)
    if assoc_crit:
        return jsonify(
            [{
                'id': assoc_crit.id,
                'nome': assoc_crit.nome
            }]
        )


@app.route('/associacao_criticos/<int:assoc_crit_id>', methods=['PUT'])
def atualizar_assoc_crit(assoc_crit_id):
    assoc_crit = Associacao_Criticos.query.get(assoc_crit_id)
    if assoc_crit:
        assoc_crit.nome = request.json.get('nome', assoc_crit.nome)
        db.session.commit()
        return jsonify(
            [{
                'id': assoc_crit.id,
                'nome': assoc_crit.nome
            }]
        )


@app.route('/associacao_criticos/<int:usuario_id_mod>/<int:assoc_crit_id>', methods=['DELETE'])
def excluir_assoc_crit(usuario_id_mod, assoc_crit_id):
    user_mod = Usuario.query.get(usuario_id_mod)
    if user_mod.permissao_moderador == True:
        assoc_crit = Associacao_Criticos.query.get(assoc_crit_id)
        if assoc_crit:
            db.session.delete(assoc_crit)
            db.session.commit()
            return '', 204
        else:
            return jsonify({'mensagem':'Associaçao de Críticos não encontrada.'}), 404

    elif user_mod.permissao_moderador == False:
        return jsonify({'mensagem':'Usuário não possui permissão para moderação.'}), 403
    else:
        return jsonify({'mensagem': 'Usuário moderador não encontrado'}), 404



@app.route('/criticas/<int:obra_id>', methods=['GET'])
def listar_criticas_filme(obra_id):
    criticas = Critica.query.all()
    return jsonify(
        [{
            'id': critica.id,
            'conteudo': critica.conteudo,
            'nota': critica.nota,
            'data': critica.data,
            'id_usuario': critica.id_usuario 
        } for critica in criticas if critica.id_obra == obra_id]
    )

@app.route('/criticas', methods=['POST'])
def cadastrar_critica():
    crit = Critica(request.json['conteudo'], request.json['nota'], request.json['data'], request.json['id_usuario'], request.json['id_obra'])
    db.session.add(crit)
    db.session.commit()
    return jsonify(
        {
            'id': crit.id,
            'conteudo': crit.conteudo,
            'nota': crit.nota,
            'data': crit.data,
            'editada': crit.editada,
            'id_usuario': crit.id_usuario
        }
    )


@app.route('/criticas/<int:critica_id>', methods=['GET'])
def buscar_critica(critica_id):
    crit = Critica.query.get(critica_id)
    if crit:
        return jsonify(
            {
                'id': crit.id,
                'conteudo': crit.conteudo,
                'nota': crit.nota,
                'data': crit.data,
                'editada': crit.editada,
                'id_usuario': crit.id_usuario
            }
        )
    
    else:
        return jsonify({'mensagem':'Critica não encontrada.'}), 404

@app.route('/criticas/<int:critica_id>', methods=['PUT'])
def atualizar_critica(critica_id):
    crit = Critica.query.get(critica_id)
    if crit:
        crit.conteudo = request.json.get('conteudo', crit.conteudo)
        crit.nota = request.json.get('nota', crit.nota)
        crit.editada = True
        db.session.commit()
        return jsonify(
            {
                'id': crit.id,
                'conteudo': crit.conteudo,
                'nota': crit.nota,
                'data': crit.data,
                'editada': crit.editada,
                'id_usuario': crit.id_usuario
            }
        )
    
    else:
        return jsonify({'mensagem':'Critica não encontrada.'}), 404



@app.route('/criticas/<int:user_id_mod>/<int:critica_id>', methods=['DELETE'])
def excluir_critica(usuario_id_mod, critica_id):
    user_mod = Usuario.query.get(usuario_id_mod)
    if user_mod.permissao_moderador == True:
        crit = Usuario.query.get(critica_id)
        if crit:
            db.session.delete(crit)
            db.session.commit()
            return '', 204
        else:
            return jsonify({'mensagem':'Crítica não encontrado.'}), 404
    elif user_mod.permissao_moderador == False:
        return jsonify({'mensagem':'Usuário não possui permissão para moderação.'}), 403
    else:
        return jsonify({'mensagem': 'Usuário moderador não encontrado'}), 404





@app.route('/obras', methods=['GET'])
def listar_obras():
    obras = Obra.query.all()
    return jsonify(
        [{
            'id': obra.id,
            'nome': obra.nome,
            'produtora': Produtora.query.get(obra.id_produtora).nome,
            'genero': obra.genero,
            'sinopse': obra.sinopse,
            'data_estreia': obra.data_estreia
        }for obra in obras]
    )


@app.route('/obras', methods=['POST'])
def cadastrar_obra():
    tipo = request.json['tipo'].upper()
    if tipo not in ['F', 'S']:
        return jsonify({'error': 'Tipo de obra inválido.'}), 400
    obra = Obra(request.json['nome'], request.json['sinopse'], request.json['genero'], request.json['id_prod'], request.json['data_estreia'], tipo)
    db.session.add(obra)
    db.session.commit()
    if tipo == 'F':
        filme = Filme(obra.id, request.json['bilheteria'])
        db.session.add(filme)
        db.session.commit()
    elif tipo == 'S':
        serie = Serie(obra.id, request.json['data_fim'], request.json['episodios'])
        db.session(serie)
        db.commit()
    return jsonify(
        [{
            'id': obra.id,
            'nome': obra.nome,
            'sinopse': obra.sinopse,
            'genero': obra.genero,
            'id_prod': obra.id_produtora,
            'data_estreia': obra.data_estreia,
            'tipo': obra.tipo
        }]
    )


@app.route('/obras/<int:obra_id>', methods=['GET'])
def buscar_obra(obra_id):
    obra = Obra.query.get(obra_id)
    if obra:
        return jsonify(
            {
                'id': obra.id,
                'nome': obra.nome,
                'produtora': Produtora.query.get(obra.id_produtora).nome,
                'genero': obra.genero,
                'sinopse': obra.sinopse,
                'data_estreia': obra.data_estreia
            }
        )
    else:
        return jsonify({'mensagem':'Obra não encontrada.'}), 404

@app.route('/obras/<int:obra_id>', methods=['PUT'])
def atualizar_obra(obra_id):
    obra = Obra.query.get(obra_id)
    if obra:
        obra.nome = request.json.get('nome', obra.nome)
        db.session.commit()
        return jsonify(
            {
                'id': obra.id,
                'nome': obra.nome,
                'produtora': Produtora.query.get(obra.id_produtora).nome,
                'genero': obra.genero,
                'sinopse': obra.sinopse,
                'data_estreia': obra.data_estreia
            }
        )
    else:
        return jsonify({'mensagem':'Obra não encontrada.'}), 404

@app.route('/obras/<int:usuario_id_mod>/<int:obra_id>', methods=['DELETE'])
def excluir_obra(usuario_id_mod, obra_id):
    user_mod = Usuario.query.get(usuario_id_mod)
    if user_mod.permissao_moderador == True:
        obra = Usuario.query.get(obra_id)
        if obra:
            db.session.delete(obra)
            db.session.commit()
            return '', 204
        else:
            return jsonify({'mensagem':'Usuario não encontrado.'}), 404
    elif user_mod.permissao_moderador == False:
        return jsonify({'mensagem':'Usuário não possui permissão para moderação.'}), 403
    else:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404



@app.route('/generos', methods=['POST'])
def cadastrar_genero():
    genero = Genero(id=request.json['id'])
    db.session.add(genero)
    db.session.commit()
    return jsonify(
        {
            'id': genero.id
        }
    )

@app.route('/generos/<int:genero_id>', methods=['DELETE'])
def excluir_genero(genero_id):
    genero = Genero.query.get(genero_id)
    if genero:
        db.session.delete(genero)
        db.session.commit()
        return '', 204
    else:
        return jsonify({'mensagem': 'Gênero não encontrado.'}), 404

@app.route('/generos/<int:genero_id>', methods=['GET'])
def buscar_genero(genero_id):
    genero = Genero.query.get(genero_id)
    if genero:
        return jsonify(
            {
                'id': genero.id
            }
        )
    else:
        return jsonify({'mensagem':'Gênero não encontrado.'}), 404
    
@app.route('/generos', methods=['GET'])
def listar_generos():
    generos = Genero.query.all()
    lista_generos = []
    for genero in generos:
        lista_generos.append({'id': genero.id})
    return jsonify(lista_generos)


@app.route('/cargos', methods=['POST'])
def cadastrar_cargo():
    cargo = Genero(id=request.json['id'])
    db.session.add(cargo)
    db.session.commit()
    return jsonify(
        {
            'id': cargo.id
        }
    )

@app.route('/cargos', methods=['GET'])
def listar_cargos():
    cargos = Cargo.query.all()
    return jsonify(
        [{
            'id':cargo.id
        } for cargo in cargos]
    )