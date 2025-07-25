import streamlit as st
import json
import os
import re

DATABASE_FILE = 'database.json'

def parse_dossie_texto(metadata, textos):
    """
    Função principal que recebe os metadados e os blocos de texto
    e retorna um dicionário JSON estruturado.
    """
    dossie = metadata.copy()
    
    # Helper para extrair valor após um título
    def extrair_valor(texto, titulo):
        padrao = re.compile(f"^{re.escape(titulo)}:(.*)", re.MULTILINE | re.IGNORECASE)
        match = padrao.search(texto)
        return match.group(1).strip() if match else "N/A"

    # Helper para extrair listas
    def extrair_lista(texto, titulo):
        padrao = re.compile(f"^{re.escape(titulo)}:(.*?)($|^\w)", re.MULTILINE | re.IGNORECASE | re.DOTALL)
        match = padrao.search(texto)
        if not match: return []
        # Extrai os itens da lista, que geralmente começam com um hífen ou número
        itens = re.findall(r"^\s*[-*0-9]+\)\s*(.*)", match.group(1), re.MULTILINE)
        return [item.strip() for item in itens] if itens else []

    # Montando o dossiê
    sumario = textos['sumario']
    base_factual = textos['base_factual']
    engrenagem = textos['engrenagem']
    sintese = textos['sintese']

    dossie['dossie_completo'] = {
        "nome_completo": metadata['clube'].replace('_', ' '),
        "url_escudo": metadata['url_escudo'],
        "sumario_estrategico": {
            "identidade_principal": extrair_valor(sumario, "Identidade Principal"),
            "padrao_quantitativo_chave": extrair_valor(sumario, "Padrão Quantitativo Chave"),
            "fator_tatico_principal": extrair_valor(sumario, "Principal Fator Tático"),
            "fator_contextual_principal": extrair_valor(sumario, "Principal Fator Contextual"),
            "cenarios_monitoramento_in_live": extrair_lista(sumario, "Cenários de Monitoramento In-Live")
        },
        "analise_profunda": {
            "base_factual": {
                "analise_quantitativa_geral": extrair_valor(base_factual, "Análise Quantitativa"),
                # Parsing mais complexo para o Raio-X pode ser adicionado aqui
                "raio_x_24_25": {"descricao_completa": base_factual}, # Simples por agora
                "analise_comparativa_elenco": extrair_valor(base_factual, "Análise Comparativa de Elenco (MAETR)")
            },
            "engrenagem_tatica": {
                "o_comandante": extrair_valor(engrenagem, "O Comandante"),
                "modelo_de_jogo": extrair_valor(engrenagem, "Modelo de Jogo"),
                "destaque_equipe": extrair_valor(engrenagem, "Destaque da Equipe")
            },
            "sintese_e_cenarios": {
                "sintese": extrair_valor(sintese, "Síntese"),
                "cenarios_detalhados": extrair_lista(sintese, "Cenários Detalhados")
            }
        }
    }
    return dossie


st.set_page_config(page_title="Editor de Dossiês", layout="wide")
st.title("📝 Editor de Dossiês Estratégicos")
st.write("Preencha os campos abaixo e cole os blocos de texto do seu dossiê para adicioná-lo ao banco de dados.")

with st.form(key="dossie_form", clear_on_submit=True):
    st.subheader("1. Informações de Identificação")
    col1, col2 = st.columns(2)
    with col1:
        pais = st.text_input("País", placeholder="Ex: Belgica")
        clube = st.text_input("Nome do Clube (use _ para espaços)", placeholder="Ex: Club_Brugge")
        temporada = st.text_input("Temporada (formato AA_AA)", placeholder="Ex: 24_25")
    with col2:
        liga = st.text_input("Liga", placeholder="Ex: Jupiler_Pro_League")
        url_escudo = st.text_input("URL do Escudo", placeholder="Cole o link da imagem do escudo aqui")
    
    st.divider()
    
    st.subheader("2. Blocos de Texto do Dossiê")
    sumario_texto = st.text_area("Cole aqui TODO o texto da 'CAMADA 1: SUMÁRIO ESTRATÉGICO'", height=200, 
        help="Inclua os títulos como 'Identidade Principal:', 'Padrão Quantitativo Chave:', etc.")
    
    base_factual_texto = st.text_area("Cole aqui TODO o texto da 'Parte 1: A Base Factual'", height=200,
        help="Inclua os títulos como 'Análise Quantitativa:', 'Raio-X de Destaques e Padrões (24/25):', etc.")

    engrenagem_texto = st.text_area("Cole aqui TODO o texto da 'Parte 2: A Engrenagem Tática'", height=150)
    
    sintese_texto = st.text_area("Cole aqui TODO o texto da 'Parte 3: Síntese e Cenários de Monitoramento'", height=150)

    submit_button = st.form_submit_button(label="Analisar, Estruturar e Salvar Dossiê")

if submit_button:
    if all([pais, liga, clube, temporada, sumario_texto, base_factual_texto, engrenagem_texto, sintese_texto]):
        metadata = {
            "pais": pais, "liga": liga, "clube": clube, 
            "temporada": temporada, "url_escudo": url_escudo
        }
        textos = {
            "sumario": sumario_texto, "base_factual": base_factual_texto,
            "engrenagem": engrenagem_texto, "sintese": sintese_texto
        }

        novo_dossie_json = parse_dossie_texto(metadata, textos)
        
        try:
            # Carrega o banco de dados existente
            if os.path.exists(DATABASE_FILE) and os.path.getsize(DATABASE_FILE) > 0:
                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                    database = json.load(f)
            else:
                database = []
            
            # Adiciona o novo dossiê
            database.append(novo_dossie_json)
            
            # Salva o banco de dados atualizado
            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=2)
            
            st.success(f"Dossiê para '{clube} ({temporada})' foi analisado e salvo no banco de dados com sucesso!")
            st.balloons()
        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar o dossiê: {e}")
            st.json(novo_dossie_json) # Mostra o JSON gerado para depuração
    else:
        st.warning("Por favor, preencha todos os campos antes de salvar.")