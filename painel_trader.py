import streamlit as st
import os
import json

# --- MOTOR DE DADOS (Atualizado para o novo fluxo com temporadas) ---
DATA_DIR = 'dados'

def listar_paises():
    if not os.path.exists(DATA_DIR): return []
    try: return sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    except Exception: return []

def listar_ligas(pais):
    caminho_pais = os.path.join(DATA_DIR, pais)
    if not os.path.exists(caminho_pais): return []
    try: return sorted([d for d in os.listdir(caminho_pais) if os.path.isdir(os.path.join(caminho_pais, d))])
    except Exception: return []

def listar_clubes(pais, liga):
    caminho_liga = os.path.join(DATA_DIR, pais, liga)
    if not os.path.exists(caminho_liga): return []
    try: return sorted([d for d in os.listdir(caminho_liga) if os.path.isdir(os.path.join(caminho_liga, d))])
    except Exception: return []

def listar_temporadas(pais, liga, clube):
    caminho_clube = os.path.join(DATA_DIR, pais, liga, clube)
    if not os.path.exists(caminho_clube): return []
    try: return sorted([d for d in os.listdir(caminho_clube) if os.path.isdir(os.path.join(caminho_clube, d))])
    except Exception: return []

def obter_dossie(pais, liga, clube, temporada):
    caminho_arquivo = os.path.join(DATA_DIR, pais, liga, clube, temporada, 'dossie.json')
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"erro": "Dossiê não encontrado. Execute o script 'gerenciador_dossie.py' para sincronizar."}

# --- FUNÇÃO PRINCIPAL DO PAINEL FINAL ---
def rodar_dossie_completo():
    st.set_page_config(page_title="Dossiê Estratégico", layout="wide", initial_sidebar_state="expanded")
    
    with st.sidebar:
        st.header("Navegação 🗺️")
        paises_disponiveis = listar_paises()
        pais = st.selectbox("País", paises_disponiveis, index=None, placeholder="Selecione o País")
        if not pais:
            st.info("Selecione um País para começar a análise.")
            return

        ligas_disponiveis = listar_ligas(pais)
        liga = st.selectbox("Liga", ligas_disponiveis, index=None, placeholder="Selecione a Liga")
        if not liga: return

        clubes_disponiveis = listar_clubes(pais, liga)
        clube = st.selectbox("Clube", clubes_disponiveis, index=None, placeholder="Selecione o Clube")
        if not clube: return
        
        temporadas_disponiveis = listar_temporadas(pais, liga, clube)
        temporada = st.selectbox("Temporada", temporadas_disponiveis, index=None, placeholder="Selecione a Temporada")
        if not temporada: return

    dados = obter_dossie(pais, liga, clube, temporada)
    if "erro" in dados:
        st.error(dados["erro"])
        return

    # --- CABEÇALHO ---
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        url_escudo = dados.get('url_escudo', '')
        if url_escudo:
            st.image(url_escudo, width=80)
    with col2:
        st.title(dados.get('nome_completo'))
        st.subheader(f"Dossiê Estratégico da Temporada {temporada.replace('_', '/')}")
    st.divider()

    # --- ABAS PRINCIPAIS ---
    tab1, tab2 = st.tabs(["**CAMADA 1: SUMÁRIO ESTRATÉGICO**", "**CAMADA 2: ANÁLISE PROFUNDA**"])

    with tab1:
        sumario = dados.get('sumario_estrategico', {})
        st.subheader("📝 Identidade Principal")
        st.write(sumario.get('identidade_principal', 'N/A'))
        st.subheader("📊 Padrão Quantitativo Chave")
        st.write(sumario.get('padrao_quantitativo_chave', 'N/A'))
        st.subheader("🧠 Principal Fator Tático")
        st.write(sumario.get('fator_tatico_principal', 'N/A'))
        st.subheader("📦 Principal Fator Contextual")
        st.write(sumario.get('fator_contextual_principal', 'N/A'))
        st.subheader("🎯 Cenários de Monitoramento In-Live")
        cenarios_live = sumario.get('cenarios_monitoramento_in_live', [])
        if cenarios_live:
            for cenario in cenarios_live:
                st.markdown(f"- {cenario}")
        else:
            st.write("N/A")

    with tab2:
        analise = dados.get('analise_profunda', {})
        
        st.markdown("### Parte 1: A Base Factual")
        base_factual = analise.get('base_factual', {})
        st.markdown(f"**Análise Quantitativa Geral:** {base_factual.get('analise_quantitativa_geral', 'N/A')}")
        st.markdown("---")
        st.markdown("##### Raio-X de Destaques e Padrões (24/25)")
        raio_x = base_factual.get('raio_x_24_25', {})
        protagonistas = raio_x.get('protagonistas', [])
        if protagonistas:
            for protagonista in protagonistas:
                st.markdown(f"**{protagonista.get('titulo', '')}:** {protagonista.get('descricao', '')}")
        else:
            st.write("N/A")
        st.markdown(f"**Padrões da Equipe:** {raio_x.get('padroes_estatisticos_equipe', 'N/A')}")
        st.markdown("---")
        st.markdown(f"**Análise Comparativa de Elenco:** {base_factual.get('analise_comparativa_elenco', 'N/A')}")
        
        st.divider()
        st.markdown("### Parte 2: A Engrenagem Tática")
        engrenagem = analise.get('engrenagem_tatica', {})
        st.markdown(f"**O Comandante:** {engrenagem.get('o_comandante', 'N/A')}")
        st.markdown(f"**Modelo de Jogo:** {engrenagem.get('modelo_de_jogo', 'N/A')}")
        st.markdown(f"**Destaque da Equipe:** {engrenagem.get('destaque_equipe', 'N/A')}")
        
        st.divider()
        st.markdown("### Parte 3: Síntese e Cenários de Monitoramento")
        sintese_cenarios = analise.get('sintese_e_cenarios', {})
        st.markdown(f"**Síntese:** {sintese_cenarios.get('sintese', 'N/A')}")
        st.markdown("**Cenários Detalhados:**")
        cenarios_det = sintese_cenarios.get('cenarios_detalhados', [])
        if cenarios_det:
            for cenario in cenarios_det:
                st.markdown(f"- {cenario}")
        else:
            st.write("N/A")

# --- PONTO DE ENTRADA ---
if __name__ == "__main__":
    rodar_dossie_completo()