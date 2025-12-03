# gerenciar_produtos.py
from app import app, db, Produto, Usuario, Carrinho, HistoricoCompra

def listar_produtos():
    """Lista todos os produtos do banco de dados"""
    with app.app_context():
        produtos = Produto.query.all()
        
        print("=" * 80)
        print("📦 LISTA DE PRODUTOS")
        print("=" * 80)
        
        if not produtos:
            print("❌ Nenhum produto encontrado!")
            return []
        
        for i, produto in enumerate(produtos, 1):
            print(f"\n{i}. ID: {produto.id}")
            print(f"   Nome: {produto.nome}")
            print(f"   Preço: R$ {produto.preco}")
            print(f"   Gênero: {produto.genero}")
            print(f"   Nacionalidade: {produto.nacionalidade}")
            print(f"   Equipe: {produto.equipe}")
            print(f"   Categoria: {produto.categoria}")
            print(f"   Descrição: {produto.descricao[:50]}..." if produto.descricao else "   Descrição: (sem descrição)")
        
        print("\n" + "=" * 80)
        return produtos

def remover_produto():
    """Remove um produto pelo ID"""
    with app.app_context():
        produtos = listar_produtos()
        
        if not produtos:
            return
        
        try:
            produto_id = int(input("\n📝 Digite o ID do produto que deseja remover (ou 0 para cancelar): "))
            
            if produto_id == 0:
                print("❌ Operação cancelada.")
                return
            
            produto = Produto.query.get(produto_id)
            
            if produto:
                # Verifica se o produto está em algum carrinho
                carrinhos = Carrinho.query.filter_by(produto_id=produto_id).all()
                historicos = HistoricoCompra.query.filter_by(produto_id=produto_id).all()
                
                print(f"\n⚠️  ATENÇÃO: Produto '{produto.nome}' será removido!")
                
                if carrinhos:
                    print(f"   Este produto está em {len(carrinhos)} carrinho(s)")
                
                if historicos:
                    print(f"   Este produto tem {len(historicos)} histórico(s) de compra")
                
                confirmacao = input("\n⚠️  Tem certeza que deseja remover? (s/n): ")
                
                if confirmacao.lower() == 's':
                    # Remove dos carrinhos primeiro
                    for carrinho in carrinhos:
                        db.session.delete(carrinho)
                    
                    # Remove dos históricos
                    for historico in historicos:
                        db.session.delete(historico)
                    
                    # Remove o produto
                    db.session.delete(produto)
                    db.session.commit()
                    
                    print(f"✅ Produto '{produto.nome}' removido com sucesso!")
                else:
                    print("❌ Remoção cancelada.")
            else:
                print(f"❌ Produto com ID {produto_id} não encontrado.")
                
        except ValueError:
            print("❌ ID inválido! Digite um número.")

def adicionar_produto():
    """Adiciona um novo produto"""
    with app.app_context():
        print("\n➕ ADICIONAR NOVO PRODUTO")
        print("-" * 40)
        
        nome = input("Nome do produto: ")
        
        # Verifica se já existe
        if Produto.query.filter_by(nome=nome).first():
            print(f"❌ Já existe um produto com o nome '{nome}'!")
            return
        
        descricao = input("Descrição: ")
        preco = float(input("Preço (ex: 199.90): "))
        genero = input("Gênero (masculino/feminino): ")
        nacionalidade = input("Nacionalidade (brasileiro/estrangeiro): ")
        equipe = input("Equipe: ")
        categoria = input("Categoria (retrô/atual): ")
        imagem = input("URL da imagem: ")
        
        novo_produto = Produto(
            nome=nome,
            descricao=descricao,
            preco=preco,
            genero=genero,
            nacionalidade=nacionalidade,
            equipe=equipe,
            categoria=categoria,
            imagem=imagem
        )
        
        db.session.add(novo_produto)
        db.session.commit()
        
        print(f"✅ Produto '{nome}' adicionado com sucesso! ID: {novo_produto.id}")

def menu_principal():
    """Menu principal de gerenciamento"""
    while True:
        print("\n" + "=" * 50)
        print("🛠️  GERENCIADOR DE PRODUTOS - FeKnight Store")
        print("=" * 50)
        print("1. 📋 Listar todos os produtos")
        print("2. ❌ Remover um produto")
        print("3. ➕ Adicionar novo produto")
        print("4. 🔍 Buscar produto por nome")
        print("5. 📊 Estatísticas")
        print("6. 🚪 Sair")
        print("=" * 50)
        
        try:
            opcao = int(input("\n👉 Escolha uma opção: "))
            
            if opcao == 1:
                listar_produtos()
            elif opcao == 2:
                remover_produto()
            elif opcao == 3:
                adicionar_produto()
            elif opcao == 4:
                buscar_produto()
            elif opcao == 5:
                mostrar_estatisticas()
            elif opcao == 6:
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida! Escolha entre 1 e 6.")
                
        except ValueError:
            print("❌ Digite um número válido!")
        except Exception as e:
            print(f"❌ Erro: {e}")

def buscar_produto():
    """Busca produto por nome ou parte do nome"""
    with app.app_context():
        termo = input("\n🔍 Digite o nome (ou parte) para buscar: ").strip().lower()
        
        produtos = Produto.query.filter(Produto.nome.ilike(f"%{termo}%")).all()
        
        if not produtos:
            print(f"❌ Nenhum produto encontrado com '{termo}'")
            return
        
        print(f"\n✅ Encontrados {len(produtos)} produto(s):")
        print("-" * 60)
        
        for i, produto in enumerate(produtos, 1):
            print(f"{i}. ID: {produto.id} | Nome: {produto.nome} | Preço: R$ {produto.preco}")

def mostrar_estatisticas():
    """Mostra estatísticas dos produtos"""
    with app.app_context():
        total_produtos = Produto.query.count()
        total_masculino = Produto.query.filter_by(genero='masculino').count()
        total_feminino = Produto.query.filter_by(genero='feminino').count()
        total_brasileiro = Produto.query.filter_by(nacionalidade='brasileiro').count()
        total_estrangeiro = Produto.query.filter_by(nacionalidade='estrangeiro').count()
        
        print("\n📊 ESTATÍSTICAS DOS PRODUTOS")
        print("-" * 40)
        print(f"📦 Total de produtos: {total_produtos}")
        print(f"👨 Produtos masculinos: {total_masculino}")
        print(f"👩 Produtos femininos: {total_feminino}")
        print(f"🇧🇷 Produtos brasileiros: {total_brasileiro}")
        print(f"🌍 Produtos estrangeiros: {total_estrangeiro}")
        
        # Equipes mais comuns
        from sqlalchemy import func
        equipes = db.session.query(
            Produto.equipe, 
            func.count(Produto.id)
        ).group_by(Produto.equipe).order_by(func.count(Produto.id).desc()).all()
        
        if equipes:
            print("\n🏆 Equipes com mais produtos:")
            for equipe, quantidade in equipes[:5]:  # Top 5
                print(f"   {equipe}: {quantidade} produto(s)")

if __name__ == "__main__":
    menu_principal()