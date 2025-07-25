import os
import json
import google.generativeai as genai
import re
import time

# Importa a função de sincronização do outro script.
try:
    from gerenciador_dossie import sincronizar_banco_para_arquivos
except ImportError:
    def sincronizar_banco_para_arquivos():
        print("\nAVISO: A função 'sincronizar_banco_para_arquivos' não foi encontrada.")
        print("Execute 'python gerenciador_dossie.py' manualmente após esta etapa.")

# --- CONFIGURAÇÃO ---
PASTA_FONTES = '_fontes'
PASTA_ARQUIVADOS = '_arquivados'
DATABASE_FILE = 'database.json'

# --- O PROMPT PARA A INTELIGÊNCIA ARTIFICIAL (Inalterado) ---
PROMPT_TEMPLATE = """
Você é um assistente de análise de dados esportivos altamente especializado. Sua única tarefa é converter o dossiê de texto fornecido em um objeto JSON perfeito, seguindo estritamente a estrutura solicitada. Não adicione comentários ou texto explicativo na sua resposta, apenas o código JSON. Se uma informação específica não estiver no texto, use um valor vazio como "" ou [].

A estrutura do objeto JSON deve ser a seguinte:
{{
  "pais": "EXTRAIR DO TEXTO OU DEIXAR EM BRANCO",
  "liga": "EXTRAIR DO TEXTO OU DEIXAR EM BRANCO",
  "clube": "EXTRAIR DO TEXTO OU DEIXAR EM BRANCO (usar _ para espaços)",
  "temporada": "EXTRAIR DO TEXTO OU DEIXAR EM BRANCO (formato AA_AA)",
  "dossie_completo": {{
    "nome_completo": "EXTRAIR DO TEXTO",
    "url_escudo": "",
    "sumario_estrategico": {{
      "identidade_principal": "EXTRAIR DO TEXTO",
      "padrao_quantitativo_chave": "EXTRAIR DO TEXTO",
      "fator_tatico_principal": "EXTRAIR DO TEXTO",
      "fator_contextual_principal": "EXTRAIR DO TEXTO",
      "cenarios_monitoramento_in_live": ["EXTRAIR LISTA DO TEXTO"]
    }},
    "analise_profunda": {{
      "base_factual": {{
        "analise_quantitativa_geral": "EXTRAIR DO TEXTO",
        "raio_x_24_25": {{
          "protagonistas": [{{"titulo": "EXTRAIR", "descricao": "EXTRAIR"}}],
          "padroes_estatisticos_equipe": "EXTRAIR"
        }},
        "analise_comparativa_elenco": "EXTRAIR"
      }},
      "engrenagem_tatica": {{
        "o_comandante": "EXTRAIR",
        "modelo_de_jogo": "EXTRAIR",
        "destaque_equipe": "EXTRAIR"
      }},
      "sintese_e_cenarios": {{
        "sintese": "EXTRAIR",
        "cenarios_detalhados": ["EXTRAIR LISTA DO TEXTO"]
      }}
    }}
  }}
}}

Com base no dossiê de texto abaixo, gere o objeto JSON correspondente.

--- INÍCIO DO DOSSIÊ DE TEXTO ---
{dossie_texto}
--- FIM DO DOSSIÊ DE TEXTO ---
"""

def processar_dossies_cli():
    """
    Versão Command-Line Interface (CLI) do processador de dossiês.
    """
    print("🤖 Iniciando Processador de Dossiês com IA (Modo CLI)...")
    
    # 1. Configurar a API Key
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("❌ ERRO: Chave de API 'GOOGLE_API_KEY' não encontrada. Configure-a e reinicie o terminal.")
            return
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"❌ ERRO ao configurar a API: {e}")
        return

    # 2. Procurar por novos arquivos de dossiê
    os.makedirs(PASTA_FONTES, exist_ok=True)
    os.makedirs(PASTA_ARQUIVADOS, exist_ok=True)
    
    arquivos_para_processar = [f for f in os.listdir(PASTA_FONTES) if f.endswith('.txt')]
    
    if not arquivos_para_processar:
        print("🟡 NENHUM novo dossiê em .txt encontrado na pasta '_fontes'.")
        return
        
    print(f"🔍 Encontrados {len(arquivos_para_processar)} dossiê(s) para processar.")
    
    # 3. Carregar o banco de dados existente
    try:
        if os.path.exists(DATABASE_FILE) and os.path.getsize(DATABASE_FILE) > 0:
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                database = json.load(f)
        else:
            database = []
    except (FileNotFoundError, json.JSONDecodeError):
        database = []

    # 4. Processar cada arquivo
    model = genai.GenerativeModel('gemini-1.5-flash')
    for nome_arquivo in arquivos_para_processar:
        caminho_arquivo = os.path.join(PASTA_FONTES, nome_arquivo)
        print(f"\nProcessing '{nome_arquivo}'...")
        
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            texto_dossie = f.read()

        prompt_completo = PROMPT_TEMPLATE.format(dossie_texto=texto_dossie)
        
        try:
            response = model.generate_content(prompt_completo)
            json_string = response.text.replace('```json', '').replace('```', '').strip()
            novo_dossie = json.loads(json_string)
            database.append(novo_dossie)
            print(f"✅ Dossiê para '{novo_dossie.get('clube', 'desconhecido')}' estruturado com sucesso!")

            os.rename(caminho_arquivo, os.path.join(PASTA_ARQUIVADOS, nome_arquivo))
            print(f"-> Arquivo '{nome_arquivo}' movido para a pasta '{PASTA_ARQUIVADOS}'.")
            time.sleep(1) # Pequena pausa para não sobrecarregar a API

        except Exception as e:
            print(f"❌ FALHA ao processar '{nome_arquivo}': {e}")

    # 5. Salvar o banco de dados atualizado
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 '{DATABASE_FILE}' atualizado com sucesso!")
    
    # 6. Chamar o sincronizador
    print("\n⚙️  Iniciando sincronização automática para o painel...")
    try:
        sincronizar_banco_para_arquivos()
    except Exception as e:
        print(f"❌ Falha na sincronização final: {e}")

    print("\n✨ Processo concluído!")

if __name__ == "__main__":
    processar_dossies_cli()