import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Produto

def adicionar_novos_produtos():
    """Adiciona novos produtos com todos os campos preenchidos"""
    with app.app_context():
        novos_produtos = [
            # PRODUTOS BRASILEIROS MASCULINOS
            {
                'nome': 'Camisa Gremio I 21/22',
                'descricao': 'Camisa Grêmio I 21/22 Torcedor Umbro Masculina - Azul+Branco',
                'preco': 123.90,
                'imagem': 'https://static.netshoes.com.br/produtos/camisa-gremio-i-2122-torcedor-umbro-masculina/58/2IA-6271-058/2IA-6271-058_zoom1.jpg?ts=1755603008&ims=1088x',
                'genero': 'masculino',
                'nacionalidade': 'brasileiro',
                'equipe': 'Gremio'
            },
            {
                'nome': 'Camisa Retrô Corinthians 1990',
                'descricao': 'Camisa Polo Retrô Corinthians 1990 Masculina - Branco+Preto',
                'preco': 212.90,
                'imagem': 'https://static.netshoes.com.br/produtos/camisa-polo-retro-corinthians-1990-masculina/28/AJM-0210-028/AJM-0210-028_zoom2.jpg?ts=1756303133&ims=1088x',
                'genero': 'masculino',
                'nacionalidade': 'brasileiro',
                'equipe': 'Corinthians'
            },
            {
                'nome': 'Camisa real madrid 2024',
                'descricao': 'Camisa Real Madrid Third 24/25 s/n° Torcedor Adidas Masculina - Cinza',
                'preco': 219.90,
                'imagem': 'https://static.netshoes.com.br/produtos/camisa-real-madrid-third-2425-sn-torcedor-adidas-masculina/38/FB9-8474-138/FB9-8474-138_zoom1.jpg?ts=1761017162&ims=1088x',
                'genero': 'masculino',
                'nacionalidade': 'estrangeiro',
                'equipe': 'real madrid'
            },
            {
                'nome': 'Camisa Retrô Real Madrid 99/00',
                'descricao': 'Camisa I Comemorativa Real Madrid 99/00 Adidas Masculina - Branco',
                'preco': 294.90,
                'imagem': 'https://static.netshoes.com.br/produtos/camisa-i-comemorativa-real-madrid-9900-adidas-masculina/14/FBA-3633-014/FBA-3633-014_zoom1.jpg?ts=1760757209&ims=1088x',
                'genero': 'masculino',
                'nacionalidade': 'estrangeiro',
                'equipe': 'Real Madrid'
            },
            {
                'nome': 'Camisa Santos 2024',
                'descricao': 'Camisa oficial do Santos - Branca listrada',
                'preco': 269.90,
                'imagem': 'santos_2024_masc.jpg',
                'genero': 'masculino',
                'nacionalidade': 'brasileiro',
                'equipe': 'Santos'
            },
            
            # PRODUTOS BRASILEIROS FEMININOS
            {
                'nome': 'Camisa Manchester City Home 23/24',
                'descricao': 'Camisa Manchester City Home 23/24 s/n° Torcedor Puma Feminina - Azul Claro+Branco',
                'preco': 259.90,
                'imagem': 'https://static.netshoes.com.br/produtos/camisa-manchester-city-home-2324-sn-torcedor-puma-feminina/38/FB9-8474-138/FB9-8474-138_zoom1.jpg?ts=1761017162&ims=1088x',
                'genero': 'feminino',
                'nacionalidade': 'estrangeiro',
                'equipe': 'manchester city'
            },
            {
                'nome': 'Camisa Finta Sampaio Corrêa III',
                'descricao': 'Camisa Finta Sampaio Corrêa III 2023 Feminina - Dourado',
                'preco': 249.90,
                'imagem': 'https://static.netshoes.com.br/produtos/camisa-finta-sampaio-correa-iii-2023-feminina/70/045-9706-070/045-9706-070_zoom1.jpg?ts=1731922407&ims=1088x',
                'genero': 'feminino',
                'nacionalidade': 'brasileiro',
                'equipe': 'sampaio correa'
            },
            
            {
                'nome': 'Camisa Masculina Betel Grêmio Retrô 1995',
                'descricao': 'Camisa Masculina Betel Grêmio Retrô 1995 Manga Curta Azul - Azul',
                'preco': 159.90,
                'imagem': 'https://static.netshoes.com.br/produtos/camisa-masculina-betel-gremio-retr-o-1995-manga-curta-azul/58/2IA-6271-058/2IA-6271-058_zoom1.jpg?ts=1755603008&ims=1088x',
                'genero': 'masculino',
                'nacionalidade': 'brasileiro',
                'equipe': 'gremio'
            }
        ]
        
        print("➕ ADICIONANDO NOVOS PRODUTOS...")
        produtos_adicionados = 0
        
        for dados_produto in novos_produtos:
            # Verifica se o produto já existe
            existe = Produto.query.filter_by(nome=dados_produto['nome']).first()
            if not existe:
                produto = Produto(**dados_produto)
                db.session.add(produto)
                produtos_adicionados += 1
                print(f"✅ {dados_produto['genero'].upper():8} | {dados_produto['nacionalidade'].upper():12} | {dados_produto['equipe']}")
            else:
                print(f"⚠️  Já existe: {dados_produto['nome']}")
        
        db.session.commit()
        print(f"\n🎉 {produtos_adicionados} NOVOS PRODUTOS ADICIONADOS!")
        
        # Estatísticas finais
        total = Produto.query.count()
        print(f"\n📊 TOTAL DE PRODUTOS NO BANCO: {total}")
        
        generos = db.session.query(Produto.genero, db.func.count(Produto.genero)).group_by(Produto.genero).all()
        print("📈 Distribuição por gênero:", dict(generos))
        
        nacionalidades = db.session.query(Produto.nacionalidade, db.func.count(Produto.nacionalidade)).group_by(Produto.nacionalidade).all()
        print("🌍 Distribuição por nacionalidade:", dict(nacionalidades))

if __name__ == '__main__':
    adicionar_novos_produtos()