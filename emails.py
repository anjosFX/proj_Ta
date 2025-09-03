from flask_mail import Message
from flask import render_template
from app import mail

# 1. Confirmação de cadastro
def enviar_confirmacao_cadastro(destino, username):
    msg = Message(
        subject="Bem-vindo à Loja de Camisas!",
        recipients=[destino],
        body=f"Olá {username}, obrigado por se cadastrar! Agora você já pode comprar suas camisas favoritas."
    )
    mail.send(msg)

# 2. Confirmação de pedido
def enviar_confirmacao_pedido(destino, pedido_id, total, itens):
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
    msg = Message(
        subject="Recuperação de Senha",
        recipients=[destino],
        body=f"Para redefinir sua senha, clique no link abaixo (válido por 30 minutos):\n{link}"
    )
    mail.send(msg)
