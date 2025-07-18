from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# CONFIGURAÇÕES DO BANCO DE DADOS
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'         # ou 'root'
app.config['MYSQL_PASSWORD'] = 'Fsdv5632'    # ou sua nova password do root
app.config['MYSQL_DB'] = 'camisas_db'

mysql = MySQL(app)

@app.route('/')
def produtos():
    # Obtém todos os produtos da tabela 'produto'
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM produto")
    produtos = cursor.fetchall()
    return render_template('produtos.html', produtos=produtos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Lê as credenciais do formulário de login
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Verifica se o usuário existe no banco de dados
        cursor.execute("SELECT * FROM usuario WHERE email = %s AND password = %s", (email, password))
        usuario = cursor.fetchone()
        if usuario:
            # Armazena o usuário na sessão e redireciona para o perfil
            session['usuario'] = usuario
            return redirect('/perfil')
        else:
            flash("Email ou Senha inválidos.")
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Lê os dados do formulário de cadastro
        username = request.form['username']
        email = request.form['email']
        password = request.form['senha']
        cursor = mysql.connection.cursor()
        # Insere um novo usuário no banco de dados
        cursor.execute("INSERT INTO usuario (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        flash('Cadastro realizado com sucesso! Faça login.')
        return redirect('/login')
    return render_template('cadastro.html')

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Atualiza os dados do perfil do usuário
        username = request.form['username']
        email = request.form['email']
        usuario_id = session['usuario']['id']
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE usuario SET username=%s, email=%s WHERE id=%s", (username, email, usuario_id))
        mysql.connection.commit()
        session['usuario']['username'] = username
        session['usuario']['email'] = email
        flash('Perfil atualizado!')
        return redirect('/perfil')

    return render_template('perfil.html', usuario=session['usuario'])

@app.route('/excluir', methods=['POST'])
def excluir():
    if 'usuario' in session:
        # Exclui a conta do usuário
        usuario_id = session['usuario']['id']
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM usuario WHERE id=%s", (usuario_id,))
        mysql.connection.commit()
        session.clear()
        flash("Conta excluída com sucesso.")
    return redirect('/login')

@app.route('/logout')
def logout():
    # Limpa a sessão do usuário
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/adicionar_carrinho', methods=['POST'])
def adicionar_carrinho():
    if 'usuario' not in session:
        return redirect('/login')
    
    user_id = session['usuario']['id']
    produto_id = request.form['produto_id']
    quantidade = int(request.form['quantidade'])

    cursor = mysql.connection.cursor()

    # Verifica se o item já está no carrinho
    cursor.execute("SELECT * FROM carrinho WHERE user_id = %s AND produto_id = %s", (user_id, produto_id))
    item = cursor.fetchone()

    if item:
        # Atualiza a quantidade se o produto já estiver no carrinho
        nova_qtd = item[3] + quantidade
        cursor.execute("UPDATE carrinho SET quantidade = %s WHERE id = %s", (nova_qtd, item[0]))
    else:
        # Adiciona o novo produto ao carrinho
        cursor.execute("INSERT INTO carrinho (user_id, produto_id, quantidade) VALUES (%s, %s, %s)", (user_id, produto_id, quantidade))

    mysql.connection.commit()
    return redirect('/')

@app.route('/carrinho')
def ver_carrinho():
    if 'usuario' not in session:
        return redirect('/login')

    user_id = session['usuario']['id']
    cursor = mysql.connection.cursor()
    # Obtém os itens do carrinho do usuário
    cursor.execute("""
        SELECT carrinho.id, produto.nome, produto.preco, carrinho.quantidade
        FROM carrinho
        JOIN produto ON carrinho.produto_id = produto.id
        WHERE carrinho.user_id = %s
    """, (user_id,))
    itens = cursor.fetchall()

    # Calcula o total do carrinho
    total = sum(item[2] * item[3] for item in itens) if itens else 0

    return render_template('carrinho.html', itens=itens, total=total)

@app.route('/remover_carrinho', methods=['POST'])
def remover_carrinho():
    # Remove um item do carrinho
    item_id = request.form['item_id']
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM carrinho WHERE id = %s", (item_id,))
    mysql.connection.commit()
    return redirect('/carrinho')

@app.route('/atualizar_carrinho_geral', methods=['POST'])
def atualizar_carrinho_geral():
    # Atualiza todos os itens do carrinho
    user_id = session['usuario']['id']
    cursor = mysql.connection.cursor()

    # Pega todos os itens do carrinho do usuário
    cursor.execute("SELECT id FROM carrinho WHERE user_id = %s", (user_id,))
    itens = cursor.fetchall()

    for item in itens:
        item_id = item[0]
        quantidade_str = request.form.get(f'quantidade_{item_id}')

        if quantidade_str is None:
            continue
        
        try:
            quantidade = int(quantidade_str)
        except ValueError:
            continue

        if quantidade > 0:
            # Atualiza a quantidade do item no carrinho
            cursor.execute("UPDATE carrinho SET quantidade = %s WHERE id = %s", (quantidade, item_id))
        else:
            # Remove o item do carrinho se a quantidade for zero
            cursor.execute("DELETE FROM carrinho WHERE id = %s", (item_id,))

    mysql.connection.commit()
    return redirect('/carrinho')

@app.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    # Atualiza todos os itens do carrinho
    user_id = session['usuario']['id']
    cursor = mysql.connection.cursor()

    # Pega todos os itens do carrinho do usuário
    cursor.execute("SELECT id FROM carrinho WHERE user_id = %s", (user_id,))
    itens = cursor.fetchall()

    for item in itens:
        item_id = item[0]
        cursor.execute("DELETE FROM carrinho WHERE id = %s", (item_id,))

    mysql.connection.commit()
    flash('Compra finalizada com sucesso!')
    return redirect('/carrinho')