from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity





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
    genero = db.Column(db.String(255))
    time = db.Column(db.String(255))
    nacionalidade = db.Column(db.String(255))
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

# Modelo para histórico de compras (para recomendações)
# Modelo para histórico de compras (para recomendações)
class HistoricoCompra(db.Model):
    __tablename__ = 'historico_compra'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_compra = db.Column(db.DateTime, default=db.func.current_timestamp())
    
class SistemaRecomendacao:
    def __init__(self):
        self.sim_df = None
        self.produto_matrix = None
        
    def gerar_matriz_compras(self):
        """Gera a matriz usuário x produto baseada no histórico de compras"""
        try:
            # Busca todos os produtos
            produtos = Produto.query.all()
            usuarios = Usuario.query.all()
            
            if len(produtos) == 0 or len(usuarios) == 0:
                print("⚠️  Não há produtos ou usuários suficientes para gerar recomendações")
                return False
            
            # Cria matriz vazia
            data = {}
            produto_nomes = []
            
            for produto in produtos:
                data[produto.nome] = [0] * len(usuarios)
                produto_nomes.append(produto.nome)
            
            # Preenche a matriz com compras do histórico
            historicos = HistoricoCompra.query.all()
            
            for historico in historicos:
                usuario_idx = next((i for i, u in enumerate(usuarios) if u.id == historico.user_id), None)
                produto = Produto.query.get(historico.produto_id)
                
                if usuario_idx is not None and produto and produto.nome in data:
                    data[produto.nome][usuario_idx] = 1  # Marca como comprado
            
            # Se não há compras, usa dados fictícios para demonstração
            if not historicos:
                print("⚠️  Usando dados de demonstração para recomendações")
                for i, produto in enumerate(produtos[:3]):  # Primeiros 3 produtos
                    for j in range(min(3, len(usuarios))):  # Primeiros 3 usuários
                        data[produto.nome][j] = 1
            
            # Cria DataFrame
            usuarios_nomes = [f"Usuario_{user.id}" for user in usuarios]
            df = pd.DataFrame(data, index=usuarios_nomes)
            
            print(f"📊 Matriz gerada: {len(produtos)} produtos x {len(usuarios)} usuários")
            
            # Calcula similaridade entre produtos
            self.produto_matrix = df.T.fillna(0)
            similaridade = cosine_similarity(self.produto_matrix)
            
            self.sim_df = pd.DataFrame(
                similaridade,
                index=self.produto_matrix.index,
                columns=self.produto_matrix.index
            )
            
            print("✅ Sistema de recomendação inicializado!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar matriz: {e}")
            return False
    
    def recomendar_produtos_similares(self, produto_nome, n=3):
        """Recomenda produtos similares baseado na similaridade"""
        try:
            if self.sim_df is None or produto_nome not in self.sim_df.columns:
                # Fallback: retorna produtos aleatórios
                produtos = Produto.query.filter(Produto.nome != produto_nome).limit(n).all()
                return produtos
            
            similares = self.sim_df[produto_nome].sort_values(ascending=False)
            similares = similares.drop(produto_nome)  # remove o próprio produto
            
            produtos_recomendados = []
            for produto_similar in similares.head(n).index:
                produto = Produto.query.filter_by(nome=produto_similar).first()
                if produto:
                    produtos_recomendados.append(produto)
            
            return produtos_recomendados
            
        except Exception as e:
            print(f"Erro na recomendação: {e}")
            # Fallback para produtos aleatórios
            produtos = Produto.query.limit(n).all()
            return produtos

# Instância global do sistema de recomendação
sistema_recomendacao = SistemaRecomendacao()


# CHATBOT CONFIG
chatbot = ChatBot(
    "LojaVirtual",
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Desculpe, não entendi. Pode reformular sua pergunta?',
            'maximum_similarity_threshold': 0.70
        }
    ],
    database_uri='sqlite:///chatbot_database.sqlite3',
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace'
    ]
)

# Treinamento
trainer = ListTrainer(chatbot)

conversas_loja = [
    "Oi", "Olá! Bem-vindo à FeKnight Store! Como posso ajudar?",
    "Ola", "Oi! Bem-vindo à nossa loja! Em que posso ser útil?",
    "Quais produtos vocês vendem?", "Vendemos camisas de alta qualidade com diversos estilos!",
    "Como funciona a troca?", "Você pode solicitar a troca em até 30 dias!",
    "Quais tamanhos disponíveis?", "Temos P, M, G e GG!",
    "Quanto custa o frete?", "O frete varia conforme sua localização!",
    "Formas de pagamento", "Aceitamos cartão, PIX e boleto!",
    "Obrigado", "Por nada! Estamos aqui para ajudar!",
    "Tchau", "Até logo! Volte sempre!"
]

print("Iniciando treinamento do chatbot...")
trainer.train(conversas_loja)
print("Chatbot treinado e pronto!")


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

    # Registra no histórico de compras para o sistema de recomendação
    for item in itens:
        historico = HistoricoCompra(
            user_id=user_id,
            produto_id=item.produto_id,
            quantidade=item.quantidade
        )
        db.session.add(historico)
    
    # Limpa carrinho
    for item in itens:
        db.session.delete(item)

    db.session.commit()
    
    # Atualiza o sistema de recomendação
    sistema_recomendacao.gerar_matriz_compras()
    
    flash('✅ Compra finalizada com sucesso! Sistema de recomendação atualizado.')
    
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


@app.route('/faq', methods=['GET', 'POST'])
def faq():
    return render_template('faq.html')

# ROTA DO CHATBOT
@app.route("/chat", methods=["POST"])
def chat_api():
    try:
        data = request.get_json()
        pergunta = data.get("mensagem", "")
        resposta = chatbot.get_response(pergunta)
        return jsonify({"resposta": str(resposta)})
    except Exception as e:
        return jsonify({"resposta": "Desculpe, estou com problemas. Tente novamente."})
    
    
@app.route('/inicializar_recomendacoes')
def inicializar_recomendacoes():
    sucesso = sistema_recomendacao.gerar_matriz_compras()
    if sucesso:
        flash('✅ Sistema de recomendação inicializado com sucesso!')
    else:
        flash('⚠️  Sistema de recomendação usando modo de demonstração')
    return redirect('/')

@app.route('/testar_recomendacao')
def testar_recomendacao():
    """Rota para testar o sistema de recomendação"""
    produtos = Produto.query.all()
    if produtos:
        recomendacoes = sistema_recomendacao.recomendar_produtos_similares(produtos[0].nome, 3)
        resultado = f"Recomendações para '{produtos[0].nome}':<br>"
        for prod in recomendacoes:
            resultado += f"- {prod.nome}<br>"
        return resultado
    return "Nenhum produto para testar"

# Rota para recomendações baseadas no usuário atual
@app.route('/recomendacoes_personalizadas')
def recomendacoes_personalizadas():
    try:
        if 'usuario' not in session:
            # Se não está logado, retorna produtos mais populares (primeiros 4)
            produtos = Produto.query.limit(4).all()
        else:
            # Para usuário logado: produtos que ele ainda não comprou
            user_id = session['usuario']['id']
            
            # Busca produtos comprados pelo usuário
            produtos_comprados_ids = db.session.query(HistoricoCompra.produto_id)\
                .filter_by(user_id=user_id)\
                .all()
            ids_comprados = [pc[0] for pc in produtos_comprados_ids]
            
            if ids_comprados:
                # Recomenda produtos similares aos que ele já comprou
                produtos_recomendados = []
                for produto_id in ids_comprados[:2]:  # Pega até 2 produtos comprados
                    produto_base = Produto.query.get(produto_id)
                    if produto_base:
                        similares = sistema_recomendacao.recomendar_produtos_similares(produto_base.nome, 2)
                        produtos_recomendados.extend(similares)
                
                # Remove duplicatas
                produtos_recomendados = list(dict.fromkeys(produtos_recomendados))
                produtos = produtos_recomendados[:4]  # Limita a 4 produtos
            else:
                # Se não comprou nada ainda, mostra produtos populares
                produtos = Produto.query.limit(4).all()
        
        # Converte para JSON
        resultados = []
        for produto in produtos:
            resultados.append({
                'id': produto.id,
                'nome': produto.nome,
                'descricao': produto.descricao,
                'preco': float(produto.preco),
                'imagem': produto.imagem
            })
        
        return jsonify(resultados)
        
    except Exception as e:
        print(f"Erro em recomendacoes_personalizadas: {e}")
        # Fallback: produtos básicos
        produtos = Produto.query.limit(4).all()
        resultados = [{
            'id': p.id,
            'nome': p.nome,
            'descricao': p.descricao,
            'preco': float(p.preco),
            'imagem': p.imagem
        } for p in produtos]
        return jsonify(resultados)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco SQLite, se não existirem
        # Inicializa o sistema de recomendação automaticamente
        print("Inicializando sistema de recomendação...")
        sistema_recomendacao.gerar_matriz_compras()
    app.run(debug=True)


