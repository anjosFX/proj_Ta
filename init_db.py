from app import app, db, Produto

def criar_popular():
    with app.app_context():   # <<< IMPORTANTE: coloca o contexto do Flask aqui
        db.create_all()

        produtos = [
           Produto(
            nome='Camisa Flamengo 24/25',
            descricao='Camisa oficial do Flamengo, temporada 2024/2025, tecido dry fit.',
            preco=249.90,
            imagem='https://imgcentauro-a.akamaihd.net/1200x1200/98698006A4.jpg'
        ),
        Produto(
            nome='Camisa Corinthians 24/25',
            descricao='Camisa oficial do Corinthians, modelo torcedor.',
            preco=229.90,
            imagem='https://imgcentauro-a.akamaihd.net/1200x1200/M147G601A5.jpg'
        ),
        Produto(
            nome='Camisa São Paulo 24/25',
            descricao='Camisa oficial do São Paulo FC, escudo bordado.',
            preco=239.90,
            imagem='https://imgcentauro-a.akamaihd.net/1300x1300/99252549A10.jpg'
        ),
        Produto(
            nome='Camisa Palmeiras 24/25',
            descricao='Camisa do Palmeiras com tecnologia drycell.',
            preco=259.90,
            imagem='https://imgcentauro-a.akamaihd.net/1200x1200/99437707A2.jpg'
        ),
        Produto(
            nome='Camisa Seleção Brasil 24/25',
            descricao='Camisa da Seleção Brasileira, modelo jogador.',
            preco=279.90,
            imagem='https://imgcentauro-a.akamaihd.net/1200x1200/995357RQA2.jpg'
        ),
            # ... seus produtos aqui
        ]

        for p in produtos:
            db.session.add(p)

        db.session.commit()
        print("Banco criado e produtos adicionados.")

if __name__ == '__main__':
    criar_popular()
    app.run(debug=True)

