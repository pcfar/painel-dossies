import os
import json

DATABASE_FILE = 'database.json'
DATA_DIR = 'dados'

def sincronizar_banco_para_arquivos():
    """
    Lê o banco de dados central e cria/atualiza a estrutura de pastas e
    arquivos que o painel Streamlit utiliza.
    """
    print("Iniciando sincronização do banco de dados para os arquivos...")

    try:
        # Garante que o arquivo exista e não esteja vazio
        if not os.path.exists(DATABASE_FILE) or os.path.getsize(DATABASE_FILE) == 0:
            print(f"AVISO: Arquivo '{DATABASE_FILE}' está vazio ou não existe. Nada a sincronizar.")
            # Cria um arquivo vazio se não existir para evitar erros futuros
            if not os.path.exists(DATABASE_FILE):
                with open(DATABASE_FILE, 'w') as f:
                    f.write('[]')
            return

        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            database = json.load(f)

    except json.JSONDecodeError:
        print(f"ERRO: Arquivo '{DATABASE_FILE}' contém um JSON inválido.")
        return

    if not isinstance(database, list):
        print("ERRO: O conteúdo do banco de dados deve ser uma lista de dossiês.")
        return

    total_dossies = len(database)
    if total_dossies == 0:
        print("Banco de dados está vazio. Nenhuma ação necessária.")
        return
        
    print(f"Encontrados {total_dossies} dossiê(s) no banco de dados.")

    # Processa cada dossiê no banco de dados
    for i, entry in enumerate(database):
        metadata_keys = ['pais', 'liga', 'clube', 'temporada', 'dossie_completo']
        if not all(key in entry for key in metadata_keys):
            print(f"AVISO: Entrada de dossiê #{i+1} está com metadados incompletos. Pulando.")
            continue

        # Cria o caminho do diretório
        caminho_final_dir = os.path.join(
            DATA_DIR,
            entry['pais'],
            entry['liga'],
            entry['clube'],
            entry['temporada']
        )
        
        # Cria as pastas se não existirem
        os.makedirs(caminho_final_dir, exist_ok=True)

        # Cria o caminho completo do arquivo dossie.json
        caminho_final_arquivo = os.path.join(caminho_final_dir, 'dossie.json')
        
        # Escreve o conteúdo do dossiê no arquivo
        with open(caminho_final_arquivo, 'w', encoding='utf-8') as f:
            json.dump(entry['dossie_completo'], f, ensure_ascii=False, indent=2)
            
        print(f"-> Dossiê '{entry['clube']} ({entry['temporada']})' sincronizado com sucesso.")

    print("\nSincronização concluída!")

if __name__ == "__main__":
    sincronizar_banco_para_arquivos()