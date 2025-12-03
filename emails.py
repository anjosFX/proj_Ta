from flask_mail import Message
from flask import render_template
from app import mail

# 1. Confirmação de cadastro
def enviar_confirmacao_cadastro(destino, username):
    """
    Envia um e-mail de confirmação de cadastro para o usuário com o nome de usuário especificado.

    Parameters:
    destino (str): E-mail do usuário que realizou o cadastro.
    username (str): Nome do usuário que realizou o cadastro.
    """
    msg = Message(
        subject="Bem-vindo à Loja de Camisas!",
        recipients=[destino],
        body=f"Olá {username}, obrigado por se cadastrar! Agora você já pode comprar suas camisas favoritas."
    )
    mail.send(msg)

# 2. Confirmação de pedido
def enviar_confirmacao_pedido(destino, pedido_id, total, itens):
    """
    Envia um e-mail de confirmação de pedido para o usuário com o ID do pedido, o total do pedido e a lista de itens.

    Parameters:
    destino (str): E-mail do usuário que realizou o pedido.
    pedido_id (int): ID do pedido.
    total (float): Total do pedido.
    itens (list): Lista de itens do pedido.
    """
    msg = Message(
        subject=f"Confirmação do Pedido #{pedido_id}",
        recipients=[destino]
    )
    msg.html = render_template(
        "emails/confirmacao_pedido.html",
        pedido_id=pedido_id,
        total=total,
        itens=itens
    )
    mail.send(msg)

# 3. Recuperação de senha
def enviar_recuperacao_senha(destino, link):
    """
    Envia um e-mail de recuperação de senha para o usuário com o link especificado.

    Parameters:
    destino (str): E-mail do usuário que realizou a recuperação de senha.
    link (str): Link para redefinir a senha.
    """
    msg = Message(
        subject="Recuperação de Senha",
        recipients=[destino],
        body=f"Para redefinir sua senha, clique no link abaixo (válido por 30 minutos):\n{link}"
    )
    mail.send(msg)
