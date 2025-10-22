from app import app, db, Produto, Carrinho

with app.app_context():
    # Ver todos os produtos
    produtos = Produto.query.all()
    for p in produtos:
        print(f"ID: {p.id} - {p.nome} - R$ {p.preco}")
    
    