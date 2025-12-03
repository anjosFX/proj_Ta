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
<<<<<<< HEAD
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from io import BytesIO  # Para criar buffer de memória
import base64

from sklearn.metrics.pairwise import cosine_similarity
=======
>>>>>>> b0c365858634ef9b51c400402a2b6361af0512bb





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
<<<<<<< HEAD
    is_admin = db.Column(db.Boolean, default=False)
=======
    genero = db.Column(db.String(255))
    time = db.Column(db.String(255))
    nacionalidade = db.Column(db.String(255))
>>>>>>> b0c365858634ef9b51c400402a2b6361af0512bb
    carrinho = relationship('Carrinho', backref='usuario', cascade='all, delete-orphan')

class Produto(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    preco = db.Column(db.Numeric(10, 2))
    genero = db.Column(db.String(50))        # masculino/feminino/unissex
    nacionalidade = db.Column(db.String(50))  # brasileiro/estrangeiro
    equipe = db.Column(db.String(100))       # nome do time
    categoria = db.Column(db.String(50))     # retrô, atual, etc.
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
        
<<<<<<< HEAD
    
        
=======
>>>>>>> b0c365858634ef9b51c400402a2b6361af0512bb
    def gerar_matriz_compras(self):
        """Gera a matriz usuário x produto baseada no histórico de compras"""
        try:
            # Busca todos os produtos
            produtos = Produto.query.all()
            usuarios = Usuario.query.all()
            
            if len(produtos) == 0 or len(usuarios) == 0:
                print("⚠️  Não há produtos ou usuários suficientes para gerar recomendações")
                return False
            
<<<<<<< HEAD
            # Cria matriz vazia com características dos produtos
            data = {}
            produto_nomes = []
            produto_features = {}  # Armazena características para recomendação baseada em conteúdo
            
            for produto in produtos:
                # Matriz de compras
                data[produto.nome] = [0] * len(usuarios)
                produto_nomes.append(produto.nome)
                
                # Características para recomendação baseada em conteúdo
                produto_features[produto.nome] = {
                    'genero': produto.genero or '',
                    'nacionalidade': produto.nacionalidade or '',
                    'equipe': produto.equipe or '',
                    'categoria': produto.categoria or ''
                }
=======
            # Cria matriz vazia
            data = {}
            produto_nomes = []
            
            for produto in produtos:
                data[produto.nome] = [0] * len(usuarios)
                produto_nomes.append(produto.nome)
>>>>>>> b0c365858634ef9b51c400402a2b6361af0512bb
            
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
            
<<<<<<< HEAD
            # Calcula similaridade entre produtos (filtragem colaborativa)
            self.produto_matrix = df.T.fillna(0)
            
            # Sistema de recomendação híbrido: combina filtragem colaborativa com baseada em conteúdo
            if len(self.produto_matrix) > 1:
                similaridade = cosine_similarity(self.produto_matrix)
                self.sim_df = pd.DataFrame(
                    similaridade,
                    index=self.produto_matrix.index,
                    columns=self.produto_matrix.index
                )
            
            # Adiciona características para recomendações baseadas em conteúdo
            self.produto_features = produto_features
=======
            # Calcula similaridade entre produtos
            self.produto_matrix = df.T.fillna(0)
            similaridade = cosine_similarity(self.produto_matrix)
            
            self.sim_df = pd.DataFrame(
                similaridade,
                index=self.produto_matrix.index,
                columns=self.produto_matrix.index
            )
>>>>>>> b0c365858634ef9b51c400402a2b6361af0512bb
            
            print("✅ Sistema de recomendação inicializado!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar matriz: {e}")
            return False
    
<<<<<<< HEAD
    
    
        def _analisar_preferencias_usuario(self, user_id):
        #Analisa as preferências do usuário baseado no histórico de compras
            try:
                # Busca produtos comprados pelo usuário
                historicos = HistoricoCompra.query.filter_by(user_id=user_id).all()
                
                if not historicos:
                    return {}
                
                # Conta frequência de características
                generos = {}
                nacionalidades = {}
                equipes = {}
                
                for historico in historicos:
                    produto = Produto.query.get(historico.produto_id)
                    if produto:
                        generos[produto.genero] = generos.get(produto.genero, 0) + historico.quantidade
                        nacionalidades[produto.nacionalidade] = nacionalidades.get(produto.nacionalidade, 0) + historico.quantidade
                        equipes[produto.equipe] = equipes.get(produto.equipe, 0) + historico.quantidade
                
                # Determina preferências mais comuns
                preferencias = {}
                if generos:
                    preferencias['genero'] = max(generos, key=generos.get)
                if nacionalidades:
                    preferencias['nacionalidade'] = max(nacionalidades, key=nacionalidades.get)
                if equipes:
                    preferencias['equipe'] = max(equipes, key=equipes.get)
                
                return preferencias
                
            except Exception as e:
                print(f"Erro ao analisar preferências: {e}")
                return {}
    
    
    
    def recomendar_produtos_similares(self, produto_nome, n=3, preferencias=None):
        """Recomenda produtos similares usando sistema híbrido"""
        try:
            recomendacoes = []
            
            # 1. Primeiro tenta recomendações colaborativas (se houver dados)
            if self.sim_df is not None and produto_nome in self.sim_df.columns:
                similares = self.sim_df[produto_nome].sort_values(ascending=False)
                similares = similares.drop(produto_nome)  # remove o próprio produto
                
                for produto_similar in similares.head(n).index:
                    produto = Produto.query.filter_by(nome=produto_similar).first()
                    if produto:
                        recomendacoes.append(produto)
            
            # 2. Se não houver recomendações colaborativas suficientes, usa baseadas em conteúdo
            if len(recomendacoes) < n and produto_nome in self.produto_features:
                produto_base = Produto.query.filter_by(nome=produto_nome).first()
                if produto_base:
                    # Busca produtos com características similares
                    produtos_similares = self._recomendar_por_caracteristicas(produto_base, n - len(recomendacoes))
                    recomendacoes.extend(produtos_similares)
            
            # 3. Remove duplicatas
            recomendacoes_unicas = []
            ids_vistos = set()
            for prod in recomendacoes:
                if prod.id not in ids_vistos:
                    ids_vistos.add(prod.id)
                    recomendacoes_unicas.append(prod)
            
            # 4. Se ainda não tiver recomendações suficientes, completa com produtos aleatórios
            if len(recomendacoes_unicas) < n:
                produtos_restantes = Produto.query.filter(
                    Produto.nome != produto_nome,
                    ~Produto.id.in_([p.id for p in recomendacoes_unicas])
                ).limit(n - len(recomendacoes_unicas)).all()
                recomendacoes_unicas.extend(produtos_restantes)
            
            return recomendacoes_unicas[:n]
=======
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
>>>>>>> b0c365858634ef9b51c400402a2b6361af0512bb
            
        except Exception as e:
            print(f"Erro na recomendação: {e}")
            # Fallback para produtos aleatórios
<<<<<<< HEAD
            produtos = Produto.query.filter(Produto.nome != produto_nome).limit(n).all()
            return produtos
    
    def _recomendar_por_caracteristicas(self, produto_base, n=3):
        """Recomenda produtos baseados em características similares"""
        try:
            # Busca produtos com as mesmas características
            produtos_similares = Produto.query.filter(
                Produto.id != produto_base.id,
                Produto.genero == produto_base.genero,
                Produto.nacionalidade == produto_base.nacionalidade
            ).limit(n * 2).all()  # Busca mais para ter opções
            
            # Se não encontrar suficientes, relaxa os critérios
            if len(produtos_similares) < n:
                produtos_similares = Produto.query.filter(
                    Produto.id != produto_base.id,
                    Produto.genero == produto_base.genero
                ).limit(n * 2).all()
            
            # Se ainda não encontrar, busca por equipe
            if len(produtos_similares) < n:
                produtos_similares = Produto.query.filter(
                    Produto.id != produto_base.id,
                    Produto.equipe == produto_base.equipe
                ).limit(n).all()
            
            return produtos_similares[:n]
            
        except Exception as e:
            print(f"Erro na recomendação por características: {e}")
            return []
    
    def recomendar_por_preferencias(self, preferencias, n=4):
        """Recomenda produtos baseados nas preferências do usuário"""
        try:
            query = Produto.query
            
            # Aplica filtros baseados nas preferências
            if preferencias.get('genero'):
                query = query.filter_by(genero=preferencias['genero'])
            
            if preferencias.get('nacionalidade'):
                query = query.filter_by(nacionalidade=preferencias['nacionalidade'])
            
            if preferencias.get('equipe'):
                query = query.filter_by(equipe=preferencias['equipe'])
            
            # Se não houver preferências específicas, recomenda baseado em histórico
            produtos = query.limit(n).all()
            
            # Se não encontrar produtos suficientes, busca produtos populares
            if len(produtos) < n:
                produtos_complementares = Produto.query.filter(
                    ~Produto.id.in_([p.id for p in produtos])
                ).limit(n - len(produtos)).all()
                produtos.extend(produtos_complementares)
            
            return produtos[:n]
            
        except Exception as e:
            print(f"Erro na recomendação por preferências: {e}")
            return Produto.query.limit(n).all()
        
sistema_recomendacao = SistemaRecomendacao()

=======
            produtos = Produto.query.limit(n).all()
            return produtos

# Instância global do sistema de recomendação
sistema_recomendacao = SistemaRecomendacao()


>>>>>>> b0c365858634ef9b51c400402a2b6361af0512bb
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

@app.route('/criar_admin')
def criar_admin():
    """Rota especial para criar o primeiro administrador"""
    # Verifica se já existe admin
    admin_existente = Usuario.query.filter_by(is_admin=True).first()
    
    if admin_existente:
        return "❌ Admin já existe!"
    
    # Cria usuário admin
    admin = Usuario(
        username='admin',
        email='admin@feknight.com',
        password='admin123',  # Senha simples para teste
        is_admin=True
    )
    
    db.session.add(admin)
    db.session.commit()
    
    return """
    ✅ Administrador criado com sucesso!<br>
    👤 Usuário: admin<br>
    🔑 Senha: admin123<br>
    ✉️ Email: admin@feknight.com<br><br>
    <a href="/login">Fazer login</a>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usuario = Usuario.query.filter_by(email=email, password=password).first()
        
        if usuario:
            session['usuario'] = {
                'id': usuario.id,
                'username': usuario.username,
                'email': usuario.email,
                'is_admin': usuario.is_admin  # Adiciona info de admin na sessão
            }
            
            # Redireciona para dashboard se for admin
            if usuario.is_admin:
                flash(f'Bem-vindo, administrador {usuario.username}!')
                return redirect('/dashboard')
            else:
                flash(f'Bem-vindo, {usuario.username}!')
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
<<<<<<< HEAD
=======

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
>>>>>>> b0c365858634ef9b51c400402a2b6361af0512bb

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
            # Se não está logado, retorna produtos baseados em características populares
            produtos = Produto.query.filter_by(
                genero='masculino',
                nacionalidade='brasileiro'
            ).limit(4).all()
        else:
            user_id = session['usuario']['id']
            
            # Busca produtos comprados pelo usuário
            produtos_comprados_ids = db.session.query(HistoricoCompra.produto_id)\
                .filter_by(user_id=user_id)\
                .all()
            ids_comprados = [pc[0] for pc in produtos_comprados_ids]
            
            if ids_comprados:
                # Analisa preferências baseadas nas compras anteriores
                preferencias = self._analisar_preferencias_usuario(user_id)
                
                # Usa o novo sistema de recomendação baseado em preferências
                produtos = sistema_recomendacao.recomendar_por_preferencias(preferencias, 4)
            else:
                # Se não comprou nada ainda, mostra produtos baseados em características gerais
                produtos = Produto.query.filter_by(genero='masculino').limit(4).all()
        
        # Converte para JSON
        resultados = []
        for produto in produtos:
            resultados.append({
                'id': produto.id,
                'nome': produto.nome,
                'descricao': produto.descricao,
                'preco': float(produto.preco),
                'imagem': produto.imagem,
                'genero': produto.genero,
                'nacionalidade': produto.nacionalidade,
                'equipe': produto.equipe
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

def _analisar_preferencias_usuario(self, user_id):
    """Analisa as preferências do usuário baseado no histórico de compras"""
    try:
        # Busca produtos comprados pelo usuário
        historicos = HistoricoCompra.query.filter_by(user_id=user_id).all()
        
        if not historicos:
            return {}
        
        # Conta frequência de características
        generos = {}
        nacionalidades = {}
        equipes = {}
        
        for historico in historicos:
            produto = Produto.query.get(historico.produto_id)
            if produto:
                generos[produto.genero] = generos.get(produto.genero, 0) + historico.quantidade
                nacionalidades[produto.nacionalidade] = nacionalidades.get(produto.nacionalidade, 0) + historico.quantidade
                equipes[produto.equipe] = equipes.get(produto.equipe, 0) + historico.quantidade
        
        # Determina preferências mais comuns
        preferencias = {}
        if generos:
            preferencias['genero'] = max(generos, key=generos.get)
        if nacionalidades:
            preferencias['nacionalidade'] = max(nacionalidades, key=nacionalidades.get)
        if equipes:
            preferencias['equipe'] = max(equipes, key=equipes.get)
        
        return preferencias
        
    except Exception as e:
        print(f"Erro ao analisar preferências: {e}")
        return {}
    
@app.route('/dashboard')
def dashboard():
    # Verifica se está logado E se é admin
    if 'usuario' not in session:
        return redirect('/login')
    
    if not session['usuario'].get('is_admin', False):
        flash('⚠️ Acesso restrito a administradores!')
        return redirect('/')
    
    # ... resto do código do dashboard ...
    
    # Coletar dados básicos de vendas
    vendas = HistoricoCompra.query.all()
    produtos = Produto.query.all()
    
    # Dados para gráfico 1: Produtos mais vendidos
    vendas_por_produto = {}
    for venda in vendas:
        produto = Produto.query.get(venda.produto_id)
        if produto:
            vendas_por_produto[produto.nome] = vendas_por_produto.get(produto.nome, 0) + venda.quantidade
    
    # Criar gráfico de barras
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Gráfico 1: Produtos mais vendidos
    if vendas_por_produto:
        produtos_nomes = list(vendas_por_produto.keys())[:5]  # Top 5
        quantidades = list(vendas_por_produto.values())[:5]
        cores = ['#00adb5', '#00fff5', '#0097a7', '#00695c', '#004d40']
        
        ax1.bar(produtos_nomes, quantidades, color=cores)
        ax1.set_title('Top 5 Produtos Mais Vendidos', color='white', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Quantidade Vendida', color='white')
        ax1.tick_params(axis='x', rotation=45, colors='white')
        ax1.tick_params(axis='y', colors='white')
        ax1.set_facecolor('#1e1e2e')
        ax1.spines['bottom'].set_color('#00adb5')
        ax1.spines['top'].set_color('#00adb5')
        ax1.spines['left'].set_color('#00adb5')
        ax1.spines['right'].set_color('#00adb5')
    else:
        ax1.text(0.5, 0.5, 'Sem dados de vendas ainda', 
                ha='center', va='center', fontsize=12, color='white')
        ax1.set_title('Top 5 Produtos Mais Vendidos', color='white')
        ax1.set_facecolor('#1e1e2e')
    
    # Gráfico 2: Distribuição de preços dos produtos
    precos = [float(p.preco) for p in produtos]
    if precos:
        ax2.hist(precos, bins=8, edgecolor='#00adb5', alpha=0.7, color='#00fff5')
        ax2.set_title('Distribuição de Preços dos Produtos', color='white', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Preço (R$)', color='white')
        ax2.set_ylabel('Número de Produtos', color='white')
        ax2.tick_params(axis='x', colors='white')
        ax2.tick_params(axis='y', colors='white')
        ax2.set_facecolor('#1e1e2e')
        ax2.spines['bottom'].set_color('#00adb5')
        ax2.spines['top'].set_color('#00adb5')
        ax2.spines['left'].set_color('#00adb5')
        ax2.spines['right'].set_color('#00adb5')
    else:
        ax2.text(0.5, 0.5, 'Sem produtos cadastrados', 
                ha='center', va='center', fontsize=12, color='white')
        ax2.set_title('Distribuição de Preços', color='white')
        ax2.set_facecolor('#1e1e2e')
    
    # Configurar fundo da figura
    fig.patch.set_facecolor('#1e1e2e')
    plt.tight_layout()
    
    # Converter gráfico para imagem base64
    img = BytesIO()
    plt.savefig(img, format='png', dpi=80, facecolor=fig.get_facecolor())
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    
    # Estatísticas simples
    total_vendas = sum(vendas_por_produto.values()) if vendas_por_produto else 0
    total_produtos = len(produtos)
    total_usuarios = Usuario.query.count()
    
    # Calcular preço médio
    if produtos:
        preco_medio = sum([float(p.preco) for p in produtos]) / len(produtos)
    else:
        preco_medio = 0
    
    return render_template('dashboard.html', 
                         plot_url=plot_url,
                         total_vendas=total_vendas,
                         total_produtos=total_produtos,
                         total_usuarios=total_usuarios,
                         preco_medio=preco_medio)

@app.route('/popular_produtos')
def popular_produtos():
    """Rota para adicionar produtos de exemplo ao banco de dados"""
    
    produtos_exemplo = [
        {
            'nome': 'Camisa Gremio I 21/22',
            'descricao': 'Camisa Grêmio I 21/22 Torcedor Umbro Masculina - Azul+Branco',
            'preco': 123.90,
            'imagem': 'https://static.netshoes.com.br/produtos/camisa-gremio-i-2122-torcedor-umbro-masculina/58/2IA-6271-058/2IA-6271-058_zoom1.jpg?ts=1755603008&ims=1088x',
            'genero': 'masculino',
            'nacionalidade': 'brasileiro',
            'equipe': 'Gremio',
            'categoria': 'atual'
        },
        {
            'nome': 'Camisa Retrô Corinthians 1990',
            'descricao': 'Camisa Polo Retrô Corinthians 1990 Masculina - Branco+Preto',
            'preco': 212.90,
            'imagem': 'https://static.netshoes.com.br/produtos/camisa-polo-retro-corinthians-1990-masculina/28/AJM-0210-028/AJM-0210-028_zoom2.jpg?ts=1756303133&ims=1088x',
            'genero': 'masculino',
            'nacionalidade': 'brasileiro',
            'equipe': 'Corinthians',
            'categoria': 'retrô'
        },
        {
            'nome': 'Camisa real madrid 2024',
            'descricao': 'Camisa Real Madrid Third 24/25 s/n° Torcedor Adidas Masculina - Cinza',
            'preco': 219.90,
            'imagem': 'https://static.netshoes.com.br/produtos/camisa-real-madrid-third-2425-sn-torcedor-adidas-masculina/38/FB9-8474-138/FB9-8474-138_zoom1.jpg?ts=1761017162&ims=1088x',
            'genero': 'masculino',
            'nacionalidade': 'estrangeiro',
            'equipe': 'real madrid',
            'categoria': 'atual'
        },
        {
            'nome': 'Camisa Retrô Real Madrid 99/00',
            'descricao': 'Camisa I Comemorativa Real Madrid 99/00 Adidas Masculina - Branco',
            'preco': 294.90,
            'imagem': 'https://static.netshoes.com.br/produtos/camisa-i-comemorativa-real-madrid-9900-adidas-masculina/14/FBA-3633-014/FBA-3633-014_zoom1.jpg?ts=1760757209&ims=1088x',
            'genero': 'masculino',
            'nacionalidade': 'estrangeiro',
            'equipe': 'Real Madrid',
            'categoria': 'retrô'
        },
        {
            'nome': 'Camisa Santos 2024',
            'descricao': 'Camisa oficial do Santos - Branca listrada',
            'preco': 269.90,
            'imagem': 'https://via.placeholder.com/300x300/FF0000/FFFFFF?text=Santos+2024',
            'genero': 'masculino',
            'nacionalidade': 'brasileiro',
            'equipe': 'Santos',
            'categoria': 'atual'
        },
        {
            'nome': 'Camisa Manchester City Home 23/24',
            'descricao': 'Camisa Manchester City Home 23/24 s/n° Torcedor Puma Feminina - Azul Claro+Branco',
            'preco': 259.90,
            'imagem': 'https://static.netshoes.com.br/produtos/camisa-manchester-city-home-2324-sn-torcedor-puma-feminina/06/2IA-6330-006/2IA-6330-006_zoom1.jpg?ts=1695213581&ims=1088x',
            'genero': 'feminino',
            'nacionalidade': 'estrangeiro',
            'equipe': 'manchester city',
            'categoria': 'atual'
        },
        {
            'nome': 'Camisa Finta Sampaio Corrêa III',
            'descricao': 'Camisa Finta Sampaio Corrêa III 2023 Feminina - Dourado',
            'preco': 249.90,
            'imagem': 'https://static.netshoes.com.br/produtos/camisa-finta-sampaio-correa-iii-2023-feminina/70/045-9706-070/045-9706-070_zoom1.jpg?ts=1731922407&ims=1088x',
            'genero': 'feminino',
            'nacionalidade': 'brasileiro',
            'equipe': 'sampaio correa',
            'categoria': 'atual'
        },
        {
            'nome': 'Camisa Masculina Betel Grêmio Retrô 1995',
            'descricao': 'Camisa Masculina Betel Grêmio Retrô 1995 Manga Curta Azul - Azul',
            'preco': 159.90,
            'imagem': 'https://static.netshoes.com.br/produtos/camisa-masculina-betel-gremio-retr-o-1995-manga-curta-azul/06/NQQ-0329-006/NQQ-0329-006_zoom1.jpg?ts=1706806527&ims=544x',
            'genero': 'masculino',
            'nacionalidade': 'brasileiro',
            'equipe': 'gremio',
            'categoria': 'retrô'
        }
    ]
    
    produtos_adicionados = 0
    for produto_data in produtos_exemplo:
        # Verifica se o produto já existe
        existe = Produto.query.filter_by(nome=produto_data['nome']).first()
        if not existe:
            novo_produto = Produto(
                nome=produto_data['nome'],
                descricao=produto_data['descricao'],
                preco=produto_data['preco'],
                imagem=produto_data['imagem'],
                genero=produto_data['genero'],
                nacionalidade=produto_data['nacionalidade'],
                equipe=produto_data['equipe'],
                categoria=produto_data['categoria']
            )
            db.session.add(novo_produto)
            produtos_adicionados += 1
    
    db.session.commit()
    
    # Atualiza o sistema de recomendação
    sistema_recomendacao.gerar_matriz_compras()
    
    return f"""
    ✅ {produtos_adicionados} produtos adicionados com sucesso!<br>
    ✨ Sistema de recomendação atualizado com as novas características.<br><br>
    <a href="/">Ver produtos</a><br>
    <a href="/testar_recomendacao">Testar sistema de recomendação</a>
    """

@app.route('/produto/<int:produto_id>')
def detalhes_produto(produto_id):
    """Página de detalhes do produto"""
    produto = Produto.query.get_or_404(produto_id)
    
    # Busca recomendações similares
    recomendacoes = sistema_recomendacao.recomendar_produtos_similares(produto.nome, 3)
    
    return render_template('detalhes_produto.html', 
                         produto=produto, 
                         recomendacoes=recomendacoes)

# API para detalhes do produto
# ADICIONE estas rotas em algum lugar ANTES do if __name__ == '__main__'

@app.route('/api/produto/<int:produto_id>')
def api_detalhes_produto(produto_id):
    """API para detalhes do produto"""
    produto = Produto.query.get_or_404(produto_id)
    return jsonify({
        'id': produto.id,
        'nome': produto.nome,
        'descricao': produto.descricao,
        'preco': float(produto.preco),
        'imagem': produto.imagem,
        'genero': produto.genero,
        'nacionalidade': produto.nacionalidade,
        'equipe': produto.equipe,
        'categoria': produto.categoria
    })

@app.route('/api/produto/<int:produto_id>/similares')
def api_produtos_similares(produto_id):
    """API para produtos similares"""
    produto = Produto.query.get_or_404(produto_id)
    similares = sistema_recomendacao.recomendar_produtos_similares(produto.nome, 4)
    
    resultado = []
    for p in similares:
        resultado.append({
            'id': p.id,
            'nome': p.nome,
            'preco': float(p.preco),
            'imagem': p.imagem
        })
    
    return jsonify(resultado)
    
    
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco SQLite, se não existirem
        # Inicializa o sistema de recomendação automaticamente
        print("Inicializando sistema de recomendação...")
        sistema_recomendacao.gerar_matriz_compras()
    app.run(debug=True)


