import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central Debug", layout="wide")

# --- CONEXÃO ---
def get_config_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Tenta ler a aba config
    return conn.read(worksheet="config", ttl=0)

def verificar_senha(senha_digitada):
    try:
        df = get_config_data()
        # Limpa espaços em branco dos nomes das colunas
        df.columns = df.columns.str.strip()
        
        # Procura a senha
        linha = df[df['chave'] == 'senha_admin']
        if not linha.empty:
            senha_real = str(linha['valor'].values[0]).strip() # Remove espaços da senha
            return senha_real == str(senha_digitada).strip()
    except:
        pass
    return senha_digitada == "admin123"

# --- INTERFACE DE LOGIN COM RAIO-X ---
st.markdown("### 🔐 Área Admin (Modo Diagnóstico)")

if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Tente fazer login aqui:")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if verificar_senha(senha):
                st.session_state['logado'] = True
                st.rerun()
            else:
                st.error("Senha Incorreta!")
    
    with col2:
        st.warning("🕵️‍♂️ RAIO-X DA PLANILHA (O que o robô vê)")
        try:
            # Tenta ler e mostrar a tabela bruta
            df_debug = get_config_data()
            st.write("**Colunas encontradas:**", df_debug.columns.tolist())
            st.write("**Dados lidos:**")
            st.dataframe(df_debug)
        except Exception as e:
            st.error(f"❌ O robô não conseguiu ler a aba 'config'. Erro: {e}")
            st.markdown("""
            **Verifique na Planilha:**
            1. A aba se chama exatamente `config` (tudo minúsculo)?
            2. Você compartilhou com o email do robô como **EDITOR**?
            """)

else:
    st.success("✅ VOCÊ ENTROU! O LOGIN FUNCIONA.")
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

