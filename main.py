from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import (current_user, LoginManager,
                             login_user, logout_user,
                             login_required)
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario_app:senhaSegura123@localhost:3306/banco'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = 'arroz eh massa'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#MODELOS 
class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    email = db.Column('usu_email', db.String(256))
    senha = db.Column('usu_senha', db.String(256))
    end = db.Column('usu_end', db.String(256))

    def __init__(self, nome, email, senha, end):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.end = end

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))
    desc = db.Column('cat_desc', db.String(256))

    def __init__ (self, nome, desc):
        self.nome = nome
        self.desc = desc

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    perguntas = db.relationship("Pergunta", backref="anuncio", cascade="all, delete-orphan")
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    preco = db.Column('anu_preco', db.Float)
    cat_id = db.Column('cat_id', db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, nome, desc, qtd, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id

class Pergunta(db.Model):
    __tablename__="pergunta"
    id = db.Column('per_id', db.Integer, primary_key = True)
    anuncio_id = db.Column('anu_id', db.Integer, db.ForeignKey("anuncio.anu_id"))
    usuario_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))
    texto = db.Column('per_texto', db.Text)
    resposta = db.Column('per_resposta', db.Text)

    def __init__(self, anuncio_id, usuario_id, texto):
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id
        self.texto = texto
#ROTAS
@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('erro404.html')

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passwd = hashlib.sha512(str(request.form.get('passwd')).encode("utf-8")).hexdigest()

        user = Usuario.query.filter_by(email=email, senha=passwd).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/usuario/novo", methods=['GET', 'POST'], endpoint="usuario_novo")
def usuario():
    mensagem = None
    if request.method == 'POST':
        hash = hashlib.sha512(request.form.get('passwd').encode('utf-8')).hexdigest()
        usuario = Usuario(
            request.form.get('user'),
            request.form.get('email'),
            hash,
            request.form.get('end')
        )
        db.session.add(usuario)
        db.session.commit()
        mensagem = "Usuário cadastrado com sucesso!"
    
    usuarios = Usuario.query.all()
    return render_template('usuario.html', usuarios=usuarios, titulo="Cadastro de Usuario", mensagem=mensagem)

@app.route("/usuario/delete/<int:id>", methods=['POST'])
@login_required
def delete_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario is None:
        mensagem = "Usuário não encontrado."
    else:
        senha_digitada = request.form.get("senha")
        senha_hash = hashlib.sha512(senha_digitada.encode('utf-8')).hexdigest()
        if senha_hash == usuario.senha:
            db.session.delete(usuario)
            db.session.commit()
            mensagem = "Usuário excluído com sucesso!"
        else:
            mensagem = "Senha incorreta! Operação não autorizada."
    usuarios = Usuario.query.all()
    return render_template('usuario.html', usuarios=usuarios, titulo="Cadastro de Usuario", mensagem=mensagem)


@app.route("/usuario/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario is None:
        return "Usuário não encontrado.", 404

    if request.method == 'POST':
        usuario.nome = request.form.get("user")
        usuario.email = request.form.get("email")
        usuario.senha = hashlib.sha512(request.form.get("passwd").encode('utf-8')).hexdigest()
        usuario.end = request.form.get("end")
        db.session.commit()
        return redirect(url_for("usuario_novo"))

    return render_template("usuario_edit.html", usuario=usuario, titulo="Editar Usuario")

@app.route("/anuncio/novo", methods=['GET', 'POST'])
@login_required
def anuncio():
    if request.method == 'POST':
        anuncio = Anuncio(
            request.form.get('nome'), 
            request.form.get('desc'),
            request.form.get('qtd'),
            request.form.get('preco'),
            request.form.get('cat'),
            current_user.id
        )
        db.session.add(anuncio)
        db.session.commit()
        return redirect(url_for('anuncio'))
    
    return render_template(
        'anuncio.html',
        anuncios=Anuncio.query.all(),
        categorias=Categoria.query.all(),
        usuarios=Usuario.query.all(),  # Passa todos os usuários para o template
        titulo="Anuncio"
    )

@app.route("/anuncio/delete/<int:id>", methods=['POST'])
@login_required
def delete_anuncio(id):
    senha_digitada = request.form.get("senha")  # senha do formulário

    anuncio = Anuncio.query.get(id)
    if anuncio is None:
        return "Anúncio não encontrado.", 404

    # Só criador ou admin podem excluir
    if (anuncio.usu_id != current_user.id) and (current_user.nome != "admin"):
        return "Você não tem permissão para excluir este anúncio.", 403

    senha_hash = hashlib.sha512(senha_digitada.encode('utf-8')).hexdigest()
    if senha_hash != current_user.senha:
        return "Senha incorreta! Operação não autorizada.", 403

    db.session.delete(anuncio)
    db.session.commit()

    return "Anúncio excluído com sucesso!", 200

@app.route("/anuncio/pergunta")
@login_required
def pergunta():
    perguntas = db.session.query(
        Pergunta.id,
        Pergunta.texto,
        Pergunta.resposta,
        Anuncio.nome.label("anuncio_nome"),
        Usuario.nome.label("usuario_nome"),
        Anuncio.usu_id.label("anuncio_dono_id")
    ).join(Anuncio, Pergunta.anuncio_id == Anuncio.id)\
     .join(Usuario, Pergunta.usuario_id == Usuario.id)\
     .all()

    return render_template(
        "pergunta.html",
        perguntas=perguntas,
        anuncios=Anuncio.query.all(),
        usuario_logado=current_user  # Passa apenas o usuário logado
    )

@app.route("/anuncio/pergunta/nova", methods=['POST'])
@login_required
def novapergunta():
    anuncio_id = request.form.get("anuncio_id")
    texto = request.form.get("texto")

    # Cria a pergunta usando o usuário logado
    pergunta = Pergunta(anuncio_id, current_user.id, texto)
    db.session.add(pergunta)
    db.session.commit()
    return redirect(url_for("pergunta"))

@app.route("/anuncio/pergunta/responder", methods=['GET', 'POST'])
@login_required
def responder():
    perguntas = []
    mensagem = None

    if request.method == 'POST':
        pergunta_id = request.form.get('pergunta_id')
        resposta = request.form.get('resposta')
        if pergunta_id and resposta:
            pergunta = Pergunta.query.get(int(pergunta_id))
            if pergunta:
                anuncio = Anuncio.query.get(pergunta.anuncio_id)
                # Só permite responder se current_user for dono do anúncio
                if anuncio.usu_id != current_user.id:
                    mensagem = "Você não pode responder perguntas de anúncios que não são seus."
                else:
                    pergunta.resposta = resposta
                    db.session.commit()
                    mensagem = "Resposta enviada com sucesso!"

    # Pega todos os anúncios do usuário logado
    anuncios = Anuncio.query.filter_by(usu_id=current_user.id).all()
    if anuncios:
        perguntas = db.session.query(
            Pergunta.id,
            Pergunta.texto,
            Pergunta.resposta,
            Pergunta.anuncio_id,
            Usuario.nome.label("usuario_nome")
        ).join(Usuario, Pergunta.usuario_id == Usuario.id)\
         .filter(Pergunta.anuncio_id.in_([a.id for a in anuncios]))\
         .all()
    else:
        mensagem = "Você não possui anúncios para responder perguntas."

    return render_template(
        "pergunta_resposta.html",
        perguntas=perguntas,
        anuncios=anuncios,
        mensagem=mensagem,
        usuario_logado=current_user
    )

@app.route("/anuncio/pergunta/excluir", methods=['POST'])
@login_required
def excluir_pergunta():
    pergunta_id = request.form.get('pergunta_id')
    pergunta = Pergunta.query.get(pergunta_id)
    if not pergunta:
        return redirect(url_for('pergunta'))

    # Só o dono do anúncio pode excluir
    anuncio = Anuncio.query.get(pergunta.anuncio_id)
    if anuncio.usu_id != current_user.id:
        return redirect(url_for('pergunta'))

    db.session.delete(pergunta)
    db.session.commit()
    return redirect(url_for('pergunta'))

@app.route("/anuncio/compra")
@login_required
def compra():
    print("Anuncio Comprado")
    return ""

@app.route("/anuncio/favoritos")
@login_required
def favoritos():
    print("Favorito Inserido")
    return ""

@app.route("/config/categoria")
@login_required
def categoria():
    return render_template('categoria.html', categorias = Categoria.query.all(), titulo='Categoria')

@app.route("/categoria/novo", methods=['POST'])
@login_required
def novacategoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/relatorios/vendas")
@login_required
def relVendas():
    return render_template('relVendas.html')

@app.route("/relatorios/compras")
@login_required
def relCompras():
    return render_template('relVCompras.html')

# INICIALIZAÇÃO
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Tabelas criadas no banco.')
    app.run(debug=True)
