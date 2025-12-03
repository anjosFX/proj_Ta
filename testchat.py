from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# Configure o chatbot para usar um approach diferente
chatbot = ChatBot(
    "LojaVirtual",
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Desculpe, não entendi. Pode reformular?',
            'maximum_similarity_threshold': 0.70
        }
    ],
    database_uri='sqlite:///test_chatbot.db',
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace'
    ]
)

# Treinamento básico em português
trainer = ListTrainer(chatbot)

conversas = [
    "Oi", "Olá! Bem-vindo à nossa loja! Como posso ajudar?",
    "Quais produtos vocês vendem?", "Vendemos camisas de alta qualidade!",
    "Como funciona a troca?", "Aceitamos trocas em até 30 dias!",
    "Quais tamanhos?", "Temos P, M, G e GG!",
    "Obrigado", "De nada! Volte sempre!",
    "Tchau", "Até logo! Obrigado pela visita!"
]

print("Treinando o chatbot...")
trainer.train(conversas)
print("Treinamento concluído!")

# Teste
print("\n🤖 Chatbot da Loja (digite 'sair' para encerrar)")
while True:
    try:
        pergunta = input("👤 Você: ")
        if pergunta.lower() in ['sair', 'exit', 'quit']:
            break
        
        resposta = chatbot.get_response(pergunta)
        print(f"🤖 Bot: {resposta}")
        
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"❌ Erro: {e}")
        break