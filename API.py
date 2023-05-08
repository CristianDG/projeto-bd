from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date
from sqlalchemy_utils import JSONType





app = Flask(__name__)

app.config['SQLALCHEMY_DATAdb.Model_URI'] = "postgresql://postgres:teste123@projetobd-aws-caju.cgsu9rzobayk.us-east-1.rds.amazonaws.com:5432/projeto_bd_caju"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Criar Classes para todas as entidades.
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String())
    senha = db.Column(db.String())
    permissao_moderador = db.Column(db.Boolean)
    id_associacao_criticos = db.Column(db.Integer, db.ForeignKey('Associacao_Criticos.id'))


    def __init__(self, nome, senha, permissao_mod, id_associacao_crit):
        self.nome = nome
        self.senha = senha
        self.permissao_moderador = permissao_mod
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
    genero = db.Column(db.String, db.ForeignKey('Genero.id'))
    sinopse = db.Column(db.String())
    data_estreia = db.Column(Date)
    relacionados = db.Column(JSONType)

    def __init__(self, nome, id_prod, genero, sinopse, data_estreia, relacionados):
        self.nome = nome
        self.id_produtora = id_prod
        self.genero = genero
        self.sinopse = sinopse
        self.data_estreia = data_estreia
        self.relacionados = relacionados
    

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
    id = db.Column(db.Integer, db.ForeignKey('Obra.id'))
    bilheteria = db.Column(db.Integer)
    
    def __init__(self, bilheteria):
        self.bilheteria = bilheteria

class Serie(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('Obra.id'))
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
    data_nascimento = db.Columnd(Date)
    foto = db.Column(db.LargeBinary())
    local_nascimento = db.Column(db.String())
    maior_nota_recebida = db.Column(db.Float)
    menor_nota_recebida = db.Column(db.FLoat)

    def __init__(self, nome, nome_art, data_nasc, foto, local_nasc, maior_nota, menor_nota):
        self.nome = nome
        self.nome_artístico = nome_art
        self.data_nascimento = data_nasc
        self.foto = foto
        self.local_nascimento = local_nasc
        self.maior_nota_recebida = maior_nota
        self.menor_nota_recebida = menor_nota
    

class Cargo(db.Model):
    id = db.Column(db.String(), primary_key="True")

    def __init__(self):
        pass



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

@app.rout('/usuarios', methods=['POST'])
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


@app.route('usuarios/<int:usuario_id_mod>/<int:usuario_id>', methods=['DELETE'])
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
