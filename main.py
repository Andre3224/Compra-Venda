from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:fusionB%C3%87@localhost:3306/banco'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# === MODELOS ===
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

# === ROTAS ===
@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('erro404.html')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/usuario/novo", methods=['GET', 'POST'], endpoint="usuario_novo")
def usuario():
    mensagem = None
    if request.method == 'POST':
        usuario = Usuario(
            request.form.get('user'),
            request.form.get('email'),
            request.form.get('passwd'),
            request.form.get('end')
        )
        db.session.add(usuario)
        db.session.commit()
        mensagem = "Usuário cadastrado com sucesso!"
    
    usuarios = Usuario.query.all()
    return render_template('usuario.html', usuarios=usuarios, titulo="Cadastro de Usuario", mensagem=mensagem)

@app.route("/usuario/delete/<int:id>", methods=['POST'])
def delete_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        mensagem = "Usuário não encontrado."
    else:
        senha_digitada = request.form.get("senha")
        if senha_digitada == usuario.senha:
            db.session.delete(usuario)
            db.session.commit()
            mensagem = "Usuário excluído com sucesso!"
        else:
            mensagem = "Senha incorreta! Operação não autorizada."
    usuarios = Usuario.query.all()
    return render_template('usuario.html', usuarios=usuarios, titulo="Cadastro de Usuario", mensagem=mensagem)


@app.route("/usuario/edit/<int:id>", methods=['GET', 'POST'])
def edit_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return "Usuário não encontrado.", 404

    if request.method == 'POST':
        usuario.nome = request.form.get("user")
        usuario.email = request.form.get("email")
        usuario.senha = request.form.get("passwd")
        usuario.end = request.form.get("end")
        db.session.commit()
        return redirect(url_for("usuario"))

    return render_template("usuario_edit.html", usuario=usuario, titulo="Editar Usuario")

@app.route("/anuncio/novo", methods=['GET', 'POST'])
def anuncio():
    if request.method == 'POST':
        anuncio = Anuncio(
            request.form.get('nome'), 
            request.form.get('desc'),
            request.form.get('qtd'),
            request.form.get('preco'),
            request.form.get('cat'),
            request.form.get('usu')
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
def delete_anuncio(id):
    senha_digitada = request.form.get("senha")  # senha do formulário

    anuncio = Anuncio.query.get(id)
    if not anuncio:
        return "Anúncio não encontrado.", 404

    usuario_criador = Usuario.query.get(anuncio.usu_id)
    if not usuario_criador:
        return "Usuário criador não encontrado.", 404

    admin_user = Usuario.query.filter_by(nome="admin").first()
    if not admin_user:
        return "Usuário admin não encontrado.", 404

    # Valida senha: admin ou dono do anúncio
    if senha_digitada == usuario_criador.senha or senha_digitada == admin_user.senha:
        db.session.delete(anuncio)
        db.session.commit()
        return "Anúncio excluído com sucesso!", 200

    return "Senha incorreta! Operação não autorizada.", 403

@app.route("/anuncio/pergunta")
def pergunta():
    return render_template('pergunta.html')

@app.route("/anuncio/compra")
def compra():
    print("Anuncio Comprado")
    return ""

@app.route("/anuncio/favoritos")
def favoritos():
    print("Favorito Inserido")
    return ""

@app.route("/config/categoria")
def categoria():
    return render_template('categoria.html', categorias = Categoria.query.all(), titulo='Categoria')

@app.route("/categoria/novo", methods=['POST'])
def novacategoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/relatorios/vendas")
def relVendas():
    return render_template('relVendas.html')

@app.route("/relatorios/compras")
def relCompras():
    return render_template('relVCompras.html')

# === INICIALIZAÇÃO ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Tabelas criadas no banco.')
    app.run(debug=True)
