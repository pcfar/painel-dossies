import os
import google.generativeai as genai

print("--- Iniciando teste de conexão com a API do Google ---")

try:
    # 1. Tenta encontrar a chave de API
    print("1/3 - Procurando a chave de API no ambiente...")
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERRO: Chave de API 'GOOGLE_API_KEY' não encontrada.")
        print("   Verifique se você reiniciou o terminal após executar o comando 'setx'.")
    else:
        print("   ... Chave de API encontrada.")
        
        # 2. Tenta configurar a biblioteca com a chave
        print("2/3 - Configurando a biblioteca Google AI...")
        genai.configure(api_key=api_key)
        print("   ... Biblioteca configurada com sucesso.")
        
        # 3. Tenta listar os modelos para forçar uma conexão real
        print("3/3 - Tentando se comunicar com os servidores do Gemini...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("   ... Comunicação estabelecida com sucesso.")
        
        print("\n✅ SUCESSO! A conexão com a API do Google está funcionando perfeitamente.")

except Exception as e:
    print(f"\n❌ FALHA: Ocorreu um erro durante o teste.")
    print(f"   Detalhes do erro: {e}")

print("\n--- Teste concluído ---")