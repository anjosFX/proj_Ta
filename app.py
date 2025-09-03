from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os




app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Configurando o banco SQLite local
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)




load_dotenv()  # carrega as variáveis do .env

# Config Flask-Mail
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=int(os.getenv('MAIL_PORT')),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS') == 'True',
    MAIL_USE_SSL=os.getenv('MAIL_USE_SSL') == 'True',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')
)

mail = Mail(app)



# Modelos (Tabelas)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255))
    carrinho = relationship('Carrinho', backref='usuario', cascade='all, delete-orphan')

class Produto(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    preco = db.Column(db.Numeric(10, 2))
    imagem = db.Column(db.String(255))
    carrinho = relationship('Carrinho', backref='produto', cascade='all, delete-orphan')

class Carrinho(db.Model):
    __tablename__ = 'carrinho'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)


# Rotas (Exemplo login, produtos, carrinho)







@app.route('/')
def produtos():
    produtos = Produto.query.all()
    return render_template('produtos.html', produtos=produtos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usuario = Usuario.query.filter_by(email=email, password=password).first()
        if usuario:
            session['usuario'] = {'id': usuario.id, 'username': usuario.username, 'email': usuario.email}
            return redirect('/perfil')
        else:
            flash('Email ou senha inválidos.')
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['senha']

        if Usuario.query.filter_by(username=username).first():
            flash('Usuário já existe.')
            return redirect('/cadastro')

        novo_usuario = Usuario(username=username, email=email, password=password)
        db.session.add(novo_usuario)
        db.session.commit()

        # Enviar e-mail de confirmação
        msg = Message(
            subject="Confirmação de Cadastro",
            recipients=[email],
            body=f"Olá {username}, seja bem-vindo à Loja de Camisas!"
        )
        mail.send(msg)

        flash('Cadastro realizado com sucesso! Verifique seu e-mail.')
        return redirect('/login')

    return render_template('cadastro.html')

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario' not in session:
        return redirect('/login')
    usuario = Usuario.query.get(session['usuario']['id'])

    if request.method == 'POST':
        usuario.username = request.form['username']
        usuario.email = request.form['email']
        db.session.commit()
        session['usuario']['username'] = usuario.username
        session['usuario']['email'] = usuario.email
        flash('Perfil atualizado!')
        return redirect('/perfil')

    return render_template('perfil.html', usuario=usuario)

@app.route('/excluir', methods=['POST'])
def excluir():
    if 'usuario' in session:
        usuario = Usuario.query.get(session['usuario']['id'])
        db.session.delete(usuario)
        db.session.commit()
        session.clear()
        flash('Conta excluída com sucesso.')
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/adicionar_carrinho', methods=['POST'])
def adicionar_carrinho():
    if 'usuario' not in session:
        return redirect('/login')
    user_id = session['usuario']['id']
    produto_id = int(request.form['produto_id'])
    quantidade = int(request.form['quantidade'])

    item = Carrinho.query.filter_by(user_id=user_id, produto_id=produto_id).first()

    if item:
        item.quantidade += quantidade
    else:
        item = Carrinho(user_id=user_id, produto_id=produto_id, quantidade=quantidade)
        db.session.add(item)

    db.session.commit()
    return redirect('/')

@app.route('/carrinho')
def ver_carrinho():
    if 'usuario' not in session:
        return redirect('/login')

    user_id = session['usuario']['id']
    itens = Carrinho.query.filter_by(user_id=user_id).all()

    total = sum(item.produto.preco * item.quantidade for item in itens)

    return render_template('carrinho.html', itens=itens, total=total)

@app.route('/remover_carrinho', methods=['POST'])
def remover_carrinho():
    item_id = int(request.form['item_id'])
    item = Carrinho.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect('/carrinho')

@app.route('/atualizar_carrinho_geral', methods=['POST'])
def atualizar_carrinho_geral():
    if 'usuario' not in session:
        return redirect('/login')

    user_id = session['usuario']['id']
    itens = Carrinho.query.filter_by(user_id=user_id).all()

    for item in itens:
        quantidade_str = request.form.get(f'quantidade_{item.id}')
        if quantidade_str is None:
            continue
        try:
            quantidade = int(quantidade_str)
        except ValueError:
            continue
        if quantidade > 0:
            item.quantidade = quantidade
        else:
            db.session.delete(item)

    db.session.commit()
    return redirect('/carrinho')

@app.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    if 'usuario' not in session:
        return redirect('/login')

    user_id = session['usuario']['id']
    itens = Carrinho.query.filter_by(user_id=user_id).all()

    for item in itens:
        db.session.delete(item)

    db.session.commit()
    flash('Compra finalizada com sucesso!')
    msg = Message(
    subject="Confirmação do Pedido",
    recipients=[session['usuario']['email']],
    body=f"Obrigado pela sua compra! Seu pedido foi confirmado."
    )
    mail.send(msg)
    return redirect('/carrinho')




@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        email = request.form['email']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            # Aqui você gera um token/link temporário
            import secrets
            token = secrets.token_urlsafe(16)
            link = f"http://localhost:5000/redefinir/{token}"

            # Envia email
            msg = Message(
                subject="Recuperação de Senha",
                recipients=[email],
                body=f"Olá, para redefinir sua senha clique no link: {link}\n(O link expira em 30 minutos)"
            )
            mail.send(msg)

            flash("Um link de recuperação foi enviado para seu e-mail.")
        else:
            flash("E-mail não encontrado.")
    return render_template('recuperar.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco SQLite, se não existirem
    app.run(debug=True)


