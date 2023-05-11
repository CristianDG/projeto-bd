from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, ForeignKey, create_engine
from sqlalchemy.orm import Mapped, Session
from sqlalchemy_utils import JSONType

import jwt
import os
from datetime import datetime as dt, timedelta
from functools import wraps
from hashlib import sha256





app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:teste123@projetobd-caju.cgsu9rzobayk.us-east-1.rds.amazonaws.com/banco_caju"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)

# Cada classe representa uma entidade do banco.
class Associacao_Criticos(db.Model):
    __tablename__ = "associacao_criticos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String())

    def __init__(self, nome):
        self.nome = nome

class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(), unique=True)
    senha = db.Column(db.String())
    permissao_moderador = db.Column(db.Boolean)
    id_associacao_criticos = db.Column(db.Integer, db.ForeignKey('associacao_criticos.id'), nullable=True)


    def __init__(self, nome, senha, permissao_mod, id_associacao_criticos):
        self.nome = nome
        self.senha = senha
        self.permissao_moderador = permissao_mod
        self.id_associacao_criticos = id_associacao_criticos




class Critica(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conteudo = db.Column(db.String())
    nota = db.Column(db.Float)
    data = db.Column(Date)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    id_obra = db.Column(db.Integer, db.ForeignKey('obra.id'))

    def __init__(self, conteudo, nota, data, id_usuario, id_obra):
        self.conteudo = conteudo
        self.nota = nota
        self.data = data
        self.id_usuario = id_usuario
        self.id_obra = id_obra

class Obra(db.Model):
    __tablename__ = "obra"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String())
    id_produtora = db.Column(db.Integer, ForeignKey('produtora.id'))
    genero = db.Column(db.String, db.ForeignKey('genero.id'), nullable=False)
    sinopse = db.Column(db.String())
    tipo = db.Column(db.String(1))
    data_estreia = db.Column(Date)


    def __init__(self, nome, id_prod, genero, sinopse, data_estreia, tipo):
        self.nome = nome
        self.id_produtora = id_prod
        self.genero = genero
        self.sinopse = sinopse
        self.data_estreia = data_estreia
        self.tipo = tipo
    

class Criticas_Obras(db.Model):
    id_obra = db.Column(db.Integer, db.ForeignKey('obra.id'), primary_key = True)
    id_critica = db.Column( db.Integer, db.ForeignKey('critica.id'), primary_key=True)

    def __init__(self):
        pass


class Genero(db.Model):
    id = db.Column(db.String(), primary_key=True)
    def __init__(self, id):
        self.id = id

class Filme(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('obra.id'), primary_key=True)
    bilheteria = db.Column(db.Integer)
    
    def __init__(self, bilheteria):
        self.bilheteria = bilheteria

class Serie(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('obra.id'), primary_key=True)
    data_fim = db.Column(Date)
    episodios = db.Column(db.Integer)

    def __init__(self, data, ep):
        self.data_fim = data
        self.episodios = ep

class Produtora(db.Model):
    __tablename__ = "produtora"
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
    #foto = db.Column(db.LargeBinary())
    local_nascimento = db.Column(db.String())

    def __init__(self, nome, nome_art, data_nasc, local_nasc):
        self.nome = nome
        self.nome_artistico = nome_art
        self.data_nascimento = data_nasc
        #self.foto = foto
        self.local_nascimento = local_nasc
    

class Cargo(db.Model):
    id = db.Column(db.String(), primary_key="True")

    def __init__(self):
        pass



def encode(dados):
    return jwt.encode(dados, 'segredo shhh...', algorithm='HS256')

def decode(dados):
    return jwt.decode(dados, 'segredo shhh...', algorithms=["HS256"])

def criptografar(senha):
    return sha256(bytes(senha ,'utf8')).hexdigest()

def autenticar(usuario=False, moderador=False, passar_usuario=False):

    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            erro = { 'error': 'não autorizado' }, 401

            if ('Authorization' not in request.headers or
                len(request.headers['Authorization'].split()) != 2):
                return erro

            token = decode(request.headers['Authorization'].split()[1])
            id_usuario = None
            try:
                id_usuario = int(token['id'])
            except:
                return erro

            ttl_token = timedelta(hours=3)

            data_token = dt.fromtimestamp(token['data'])
            agora = dt.now()


            if (agora - data_token) > ttl_token:
                return {'error': 'token expirado'}, 403

            user = Usuario.query.get(id_usuario)
            if not user:
                return erro

            if (moderador and not user.permissao_moderador) and (moderador and user.permissao_moderador):
                return erro

            if passar_usuario:
                return fn(*args, **kwargs, usuario_solicitante=user)
            return fn(*args, **kwargs)

        return inner
    return wrapper

@app.errorhandler(Exception)
def handle_bad_request(e):
    raise e
    print(e)
    return {'error': 'erro interno do servidor'}, 500

@app.post('/login')
def login():
    usuario_json = request.get_json()

    usuario = db.session.execute(
        db.select(Usuario)
        .where(Usuario.nome == usuario_json.get('nome') and
               Usuario.senha == criptografar(usuario_json.get('senha')))
        ).scalar_one()

    if not usuario:
        return {'error': 'email ou senha incorretos'}, 400

    now = dt.now()
    token = encode({'id': usuario.id, 'data': now.timestamp()})

    return { 'token': token }, 200

# Rotas da API

# *************ROTAS DE USUÁRIO****************************
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
    user = Usuario(
        request.json['nome'],
        request.json['senha'],
        request.json['permissao_moderador'],
        request.json['id_associacao_criticos']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'id':user.id,
        'nome':user.nome,
        'permissão_moderador':user.permissao_moderador,
        'associação_criticos':user.id_associacao_criticos
    })


@app.route('/usuarios/<int:usuario_id>', methods=['GET'])
def buscar_usuario(usuario_id):
    user = Usuario.query.get(usuario_id)
    if not user:
        return jsonify({'mensagem':'Usuario não encontrado.'}), 404
    return jsonify({
        'id':user.id,
        'nome':user.nome,
        'permissão_moderador':user.permissao_moderador,
        'associação_criticos':user.id_associacao_criticos
    })


@app.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def atualizar_usuario(usuario_id):
    user = Usuario.query.get(usuario_id)
    if not user:
        return jsonify({'mensagem':'Usuario não encontrado.'}), 404

    user.nome = request.json.get('nome', user.nome)
    db.session.commit()
    return jsonify({
        'id':user.id,
        'nome':user.nome,
        'permissão_moderador':user.permissao_moderador,
        'associação_criticos':user.id_associacao_criticos
    })


@app.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
@autenticar(moderador=True)
def excluir_usuario(usuario_id):
    user = Usuario.query.get(usuario_id)
    if not user:
        return {'mensagem': 'Usuário não encontrado'}, 404
    db.session.delete(user)
    db.session.commit()
    return '', 204

# *************ROTAS DE USUÁRIO****************************



# *************ROTAS DE ASSOCIACAO CRITICOS****************************
@app.route('/associacao_criticos', methods=['GET'])
def listar_assoc_criticos():
    assoc_crits = Associacao_Criticos.query.all()
    return jsonify(
        [{
            'id': assoc_critic.id,
            'nome': assoc_critic.nome
        } for assoc_critic in assoc_crits]
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
    if not assoc_crit:
        return jsonify({'mensagem': 'Associação de críticos não encontrada'}), 404

    return jsonify({
        'id': assoc_crit.id,
        'nome': assoc_crit.nome
    })


@app.route('/associacao_criticos/<int:assoc_crit_id>', methods=['PUT'])
def atualizar_assoc_crit(assoc_crit_id):
    assoc_crit = Associacao_Criticos.query.get(assoc_crit_id)
    if not assoc_crit:
        return jsonify({'mensagem': 'Associação de críticos não encontrada'}), 404
    assoc_crit.nome = request.json.get('nome', assoc_crit.nome)
    db.session.commit()
    return jsonify({
        'id': assoc_crit.id,
        'nome': assoc_crit.nome
    })


@app.route('/associacao_criticos/<int:assoc_crit_id>', methods=['DELETE'])
@autenticar(moderador=True)
def excluir_assoc_crit(assoc_crit_id):
    assoc_crit = Associacao_Criticos.query.get(assoc_crit_id)
    if not assoc_crit:
        return jsonify({'mensagem':'Associaçao de Críticos não encontrada.'}), 404
    db.session.delete(assoc_crit)
    db.session.commit()
    return '', 204


# *************ROTAS DE ASSOCIACAO CRITICOS****************************



# *************ROTAS DE CRITICA****************************
@app.route('/criticas/<int:obra_id>', methods=['GET'])
def listar_criticas_filme(obra_id):

    critica = db.session.execute(
        db.select(Critica)
        .where(Critica.id_obra == id_obra)
        .limit(1)).scalar_one()

    return jsonify({
        'id': critica.id,
        'conteudo': critica.conteudo,
        'nota': critica.nota,
        'data': critica.data,
        'id_usuario': critica.id_usuario
    })

@app.route('/criticas', methods=['POST'])
def cadastrar_critica():
    crit = Critica(
        request.json['conteudo'],
        request.json['nota'],
        dt.now(),
        request.json['id_usuario'],
        request.json['id_obra'])

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



@app.route('/criticas/<int:critica_id>', methods=['DELETE'])
@autenticar(moderador=True)
def excluir_critica(critica_id):
    crit = Usuario.query.get(critica_id)
    if crit:
        db.session.delete(crit)
        db.session.commit()
        return '', 204
    else:
        return jsonify({'mensagem':'Crítica não encontrado.'}), 404

# *************ROTAS DE CRITICA****************************


# *************ROTAS DE OBRA****************************
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

@app.route('/produtoras', methods=['POST'])
def cadastrar_produtora():
    prod = Produtora(request.json['nome'])

    db.session.add(prod)
    db.session.commit()
    return jsonify({
        'id': prod.id,
        'nome': prod.nome
    })

@app.route('/obras', methods=['POST'])
def cadastrar_obra():
    tipo = request.json['tipo'].upper()
    if tipo not in ['F', 'S']:
        return jsonify({'error': 'Tipo de obra inválido.'}), 400
    obra = Obra(
        nome=request.json['nome'],
        sinopse=request.json['sinopse'],
        genero=request.json['genero'],
        id_prod=request.json['id_prod'],
        data_estreia=dt.fromtimestamp(request.json['data_estreia']),
        tipo=tipo)
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
        {
            'id': obra.id,
            'nome': obra.nome,
            'sinopse': obra.sinopse,
            'genero': obra.genero,
            'id_prod': obra.id_produtora,
            'data_estreia': obra.data_estreia,
            'tipo': obra.tipo
        }
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

@app.route('/obras/<int:obra_id>', methods=['DELETE'])
@autenticar(moderador=True)
def excluir_obra(obra_id):
    obra = Usuario.query.get(obra_id)
    if obra:
        db.session.delete(obra)
        db.session.commit()
        return '', 204
    else:
        return jsonify({'mensagem':'Obra não encontrada.'}), 404

# *************ROTAS DE OBRA****************************



# *************ROTAS DE GENERO****************************
@app.route('/generos', methods=['POST'])
def cadastrar_genero():
    genero = Genero(id=request.json['nome'])
    db.session.add(genero)
    db.session.commit()
    return jsonify(
        {
            'nome': genero.id
        }
    )

@app.route('/generos/<int:genero_id>', methods=['DELETE'])
@autenticar(moderador=True)
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
                'nome': genero.id
            }
        )
    else:
        return jsonify({'mensagem':'Gênero não encontrado.'}), 404
    
@app.route('/generos', methods=['GET'])
def listar_generos():
    generos = Genero.query.all()
    lista_generos = []
    for genero in generos:
        lista_generos.append({'nome': genero.id})
    return jsonify(lista_generos)

# *************ROTAS DE GENERO****************************

# *************ROTAS DE STAFF****************************
@app.route('/staff', methods=['POST'])
def cadastrar_staff():
    nome = request.json['nome']
    nome_artistico = request.json['nome_artistico']
    data_nascimento = dt.strptime(request.json['data_nascimento'], '%Y-%m-%d').date()
    #foto = request.json['foto']
    local_nascimento = request.json['local_nascimento']

    novo_staff = Staff(nome, nome_artistico, data_nascimento, local_nascimento)
    db.session.add(novo_staff)
    db.session.commit()

    return jsonify({'id': novo_staff.id})

@app.route('/staff/<int:staff_id>', methods=['DELETE'])
def excluir_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if staff:
        db.session.delete(staff)
        db.session.commit()
        return '', 204
    else:
        return jsonify({'mensagem': 'Staff não encontrado.'}), 404
    
@app.route('/staff/<int:staff_id>', methods=['GET'])
def buscar_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if staff:
        return jsonify({
            'id': staff.id,
            'nome': staff.nome,
            'nome_artistico': staff.nome_artístico,
            'data_nascimento': str(staff.data_nascimento),
            'local_nascimento': staff.local_nascimento
        })
    else:
        return jsonify({'mensagem': 'Staff não encontrado.'}), 404
    
@app.route('/staff', methods=['GET'])
def listar_staffs():
    staffs = Staff.query.all()
    lista_staffs = []
    for staff in staffs:
        lista_staffs.append({
            'id': staff.id,
            'nome': staff.nome,
            'nome_artistico': staff.nome_artístico,
            'data_nascimento': str(staff.data_nascimento),
            'local_nascimento': staff.local_nascimento
        })
    return jsonify(lista_staffs)

# *************ROTAS DE STAFF****************************

# *************ROTAS DE CARGO****************************
@app.route('/cargos', methods=['POST'])
def cadastrar_cargo():
    id = request.json['nome']
    novo_cargo = Cargo(id=id)
    db.session.add(novo_cargo)
    db.session.commit()
    return jsonify({'nome': novo_cargo.id})

@app.route('/cargos', methods=['GET'])
def listar_cargos():
    cargos = Cargo.query.all()
    lista_cargos = []
    for cargo in cargos:
        lista_cargos.append({
            'nome': cargo.id
        })
    return jsonify(lista_cargos)

# *************ROTAS DE CARGO****************************
