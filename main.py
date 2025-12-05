import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Central de Experiência",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONEXÃO COM GOOGLE SHEETS ---
def get_feedback_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet="Página1", ttl=0)

def get_config_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        df = conn.read(worksheet="config", ttl=0)
        # BLINDAGEM: Remove espaços invisíveis dos nomes das colunas
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

def salvar_feedback(nome, nota, motivo, categoria):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        data_atual = get_feedback_data()
        
        nova_linha = pd.DataFrame([{
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nome": nome if nome else "Anônimo",
            "nota": int(nota),
            "motivo": motivo,
            "categoria": categoria
        }])
        
        df_final = pd.concat([data_atual, nova_linha], ignore_index=True)
        conn.update(worksheet="Página1", data=df_final)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def verificar_senha(senha_digitada):
    df_config = get_config_data()
    if not df_config.empty:
        try:
            # Garante que lê como texto e remove espaços
            linha = df_config[df_config['chave'] == 'senha_admin']
            if not linha.empty:
                senha_real = str(linha['valor'].values[0]).strip()
                return senha_real == str(senha_digitada).strip()
        except:
            pass
    return senha_digitada == "admin123"

def alterar_senha(nova_senha):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_config = get_config_data()
        
        # Atualiza o valor
        df_config.loc[df_config['chave'] == 'senha_admin', 'valor'] = nova_senha
        conn.update(worksheet="config", data=df_config)
        return True
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        return False

# --- ASSETS ---
HERO_IMAGE_URL = "https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=2070&auto=format&fit=crop"
BOT_AVATAR_URL = "https://api.iconify.design/fluent:bot-24-filled.svg?color=%232563EB"
USER_AVATAR_URL = "https://api.iconify.design/solar:user-circle-bold.svg?color=%23475569"

# --- CHATBOT ---
BASE_CONHECIMENTO = {
    "horario": "Nosso atendimento é de Segunda a Sexta, das 09h às 18h.",
    "preço": "Planos a partir de R$ 99,90/mês.",
    "reembolso": "Solicite via financeiro@empresa.com em até 7 dias.",
    "local": "Av. Paulista, 1000 - São Paulo.",
    "default": "Não entendi. Tente perguntar sobre: horário, preço ou local."
}
def responder_bot(msg):
    msg = msg.lower()
    for k, v in BASE_CONHECIMENTO.items():
        if k in msg: return v
    return BASE_CONHECIMENTO["default"]

# --- CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    .stApp {background-color: #F8FAFC;}
    #MainMenu, footer, header {visibility: hidden;}
    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 4rem 2rem; border-radius: 0 0 24px 24px; color: white; margin-bottom: 3rem;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.2);
    }
    .hero-title {font-size: 3rem; font-weight: 800; margin-bottom: 1rem;}
    .content-card {background-color: #FFFFFF; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;}
    .stButton>button {background: linear-gradient(90deg, #2563EB, #4F46E5); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; width: 100%; transition: 0.2s;}
    .stButton>button:hover {transform: translateY(-2px); box-shadow: 0 8px 15px rgba(37, 99, 235, 0.25);}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {border-radius: 8px; border: 1px solid #CBD5E1; padding: 10px;}
    .stTabs [aria-selected="true"] {color: #2563EB; border-bottom: 3px solid #2563EB;}
    .stChatMessage .stChatMessageAvatar {background-color: transparent !important; width: 45px; height: 45px;}
    div[data-testid="stChatMessageContent"] {background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;}
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DO APP ---
query_params = st.query_params
modo_admin = query_params.get("acesso") == "admin"

if modo_admin:
    # === ÁREA ADMIN ===
    st.markdown("### 🔒 Gestão Integrada")
    
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False

    if not st.session_state['logado']:
        c1, c2, c3 = st.columns([1,1,1])
        with c2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.info("Acesso Restrito")
            senha_digitada = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                # Debug silencioso: printa no console se houver erro
                if verificar_senha(senha_digitada):
                    st.session_state['logado'] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        tab_dash, tab_conf = st.tabs(["📊 Dashboard", "⚙️ Configurações"])
        
        with tab_dash:
            try:
                df = get_feedback_data()
                if not df.empty and 'nota' in df.columns:
                    total = len(df)
                    media = df['nota'].mean()
                    ultimo = df['data'].iloc[-1] if 'data' in df.columns else "Agora"
                    
                    k1, k2, k3 = st.columns(3)
                    k1.metric("Total", total); k2.metric("Média", f"{media:.1f}"); k3.metric("Última", ultimo)
                    st.divider()
                    c1, c2 = st.columns(2)
                    if 'categoria' in df.columns: c1.bar_chart(df['categoria'].value_counts(), color="#3B82F6")
                    if 'nota' in df.columns: c2.line_chart(df['nota'], color="#6366F1")
                    
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("Sem dados ainda.")
            except:
                st.warning("Conectando...")

        with tab_conf:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.warning("Alteração de Senha de Acesso")
            n1 = st.text_input("Nova Senha", type="password")
            n2 = st.text_input("Confirme a Nova Senha", type="password")
            if st.button("Salvar Nova Senha"):
                if n1 == n2 and n1:
                    if alterar_senha(n1): st.success("✅ Senha alterada!")
                else:
                    st.error("Erro na validação.")
            st.markdown("---")
            if st.button("Sair (Logout)"):
                st.session_state['logado'] = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # === ÁREA PÚBLICA ===
    st.markdown(f"""
        <div class="hero-container">
            <div style="display: flex; align-items: center; justify-content: space-between; max-width: 1200px; margin: 0 auto; gap: 2rem;">
                <div style="flex: 1;">
                    <h1 class="hero-title">Central de <br>Sucesso do Cliente</h1>
                    <p style="font-size: 1.2rem; opacity: 0.9;">Canal oficial. Seus dados são salvos com segurança.</p>
                </div>
                <div style="flex: 1; text-align: right;">
                    <img src="{HERO_IMAGE_URL}" style="border-radius: 16px; width: 100%; max-height: 300px; object-fit: cover; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        c_l, c_main, c_r = st.columns([1, 8, 1])
        with c_main:
            tab_chat, tab_form = st.tabs(["🤖 Assistente Virtual", "⭐ Avaliar Experiência"])
            
            with tab_chat:
                st.write("")
                if "msgs" not in st.session_state: st.session_state.msgs = [{"role":"assistant", "content":"Olá! Sou a IA da empresa. Como posso ajudar?"}]
                for m in st.session_state.msgs:
                    av = BOT_AVATAR_URL if m["role"]=="assistant" else USER_AVATAR_URL
                    with st.chat_message(m["role"], avatar=av): st.write(m["content"])
                if p := st.chat_input("Dúvida?"):
                    st.session_state.msgs.append({"role":"user", "content":p})
                    with st.chat_message("user", avatar=USER_AVATAR_URL): st.write(p)
                    time.sleep(0.4)
                    r = responder_bot(p)
                    st.session_state.msgs.append({"role":"assistant", "content":r})
                    with st.chat_message("assistant", avatar=BOT_AVATAR_URL): st.write(r)

            with tab_form:
                st.write("")
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.subheader("Sua opinião importa")
                with st.form("feed_form"):
                    c1, c2 = st.columns(2)
                    with c1: nome = st.text_input("Nome (Opcional)")
                    with c2: cat = st.selectbox("Assunto *", ["", "Elogio", "Sugestão", "Reclamação", "Dúvida"], format_func=lambda x: "Selecione..." if x == "" else x)
                    nota = st.slider("Nota", 1, 10, 10)
                    motivo = st.text_area("Mensagem", placeholder="Escreva aqui...")
                    st.write("")
                    priv = st.checkbox("Concordo com a Política de Privacidade.")
                    
                    if st.form_submit_button("Enviar Avaliação"):
                        if not priv: st.error("Aceite a privacidade.")
                        elif cat == "": st.error("Escolha um Assunto.")
                        else:
                            if salvar_feedback(nome, nota, motivo, cat):
                                st.success("✅ Feedback enviado!")
                                st.markdown("**Obrigado por enviar.** Sua opinião é muito importante para nós.")
                st.markdown('</div>', unsafe_allow_html=True)

