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

# --- CONEXÃO COM GOOGLE SHEETS (BANCO DE DADOS ETERNO) ---
def get_data():
    """Lê os dados da planilha e retorna um DataFrame limpo"""
    # Cria a conexão usando os segredos que você configurou
    conn = st.connection("gsheets", type=GSheetsConnection)
    # TTL=0 garante que não pegamos dados velhos do cache
    return conn.read(ttl=0)

def salvar_feedback(nome, nota, motivo, categoria):
    """Adiciona uma nova linha na planilha"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        data_atual = get_data()
        
        # Cria a nova linha com os dados do formulário
        nova_linha = pd.DataFrame([{
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nome": nome if nome else "Anônimo",
            "nota": int(nota),
            "motivo": motivo,
            "categoria": categoria
        }])
        
        # Junta o antigo com o novo e atualiza a planilha
        df_atualizado = pd.concat([data_atual, nova_linha], ignore_index=True)
        conn.update(data=df_atualizado)
        return True
    except Exception as e:
        st.error(f"Erro de conexão. Verifique se o robô é Editor da planilha. Detalhe: {e}")
        return False

# --- ASSETS VISUAIS ---
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

# --- CSS PREMIUM ---
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
    # === ÁREA ADMIN (Conectada ao Google Sheets) ===
    st.markdown("### 🔒 Gestão Integrada")
    
    # Login fixo para facilitar (pode melhorar depois)
    senha = st.text_input("Senha Mestra", type="password")
    
    if senha == "admin123":
        try:
            df = get_data()
            
            if not df.empty and 'nota' in df.columns:
                total = len(df)
                media = df['nota'].mean()
                ultimo = df['data'].iloc[-1] if 'data' in df.columns else "Agora"
                
                k1, k2, k3 = st.columns(3)
                k1.metric("Total", total)
                k2.metric("Média", f"{media:.1f}")
                k3.metric("Última Interação", ultimo)
                
                st.divider()
                
                c1, c2 = st.columns(2)
                if 'categoria' in df.columns:
                    c1.bar_chart(df['categoria'].value_counts(), color="#3B82F6")
                if 'nota' in df.columns:
                    c2.line_chart(df['nota'], color="#6366F1")
                
                st.dataframe(df, use_container_width=True)
            else:
                st.info("A planilha está conectada, mas ainda não tem dados de feedback.")
                
        except Exception as e:
            st.warning("Conectando à planilha... Se demorar, verifique se o email do robô é 'Editor' no Google Sheets.")
            
    elif senha:
        st.error("Senha incorreta.")

else:
    # === ÁREA PÚBLICA (Visual Tech Azul) ===
    st.markdown(f"""
        <div class="hero-container">
            <div style="display: flex; align-items: center; justify-content: space-between; max-width: 1200px; margin: 0 auto; gap: 2rem;">
                <div style="flex: 1;">
                    <h1 class="hero-title">Central de <br>Sucesso do Cliente</h1>
                    <p style="font-size: 1.2rem; opacity: 0.9;">
                        Canal oficial. Seus dados são salvos com segurança na nuvem.
                    </p>
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
            
            # CHAT
            with tab_chat:
                st.write("")
                if "msgs" not in st.session_state: st.session_state.msgs = [{"role":"assistant", "content":"Olá! Sou a IA da empresa. Como posso ajudar?"}]
                for m in st.session_state.msgs:
                    avatar_icon = BOT_AVATAR_URL if m["role"] == "assistant" else USER_AVATAR_URL
                    with st.chat_message(m["role"], avatar=avatar_icon): st.write(m["content"])
                
                if prompt := st.chat_input("Digite sua dúvida..."):
                    st.session_state.msgs.append({"role":"user", "content":prompt})
                    with st.chat_message("user", avatar=USER_AVATAR_URL): st.write(prompt)
                    time.sleep(0.4)
                    resp = responder_bot(prompt)
                    st.session_state.msgs.append({"role":"assistant", "content":resp})
                    with st.chat_message("assistant", avatar=BOT_AVATAR_URL): st.write(resp)

            # FORMULÁRIO (SALVA NO GOOGLE)
            with tab_form:
                st.write("")
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.subheader("Sua opinião importa")
                
                with st.form("feed_form"):
                    c1, c2 = st.columns(2)
                    with c1: nome = st.text_input("Nome (Opcional)")
                    with c2: 
                        cat = st.selectbox("Assunto *", ["", "Elogio", "Sugestão", "Reclamação", "Dúvida"], format_func=lambda x: "Selecione..." if x == "" else x)
                    
                    nota = st.slider("Nota de Satisfação", 1, 10, 10)
                    motivo = st.text_area("Mensagem", placeholder="Escreva aqui...")
                    
                    st.write("")
                    priv = st.checkbox("Concordo com a Política de Privacidade.")
                    
                    sub = st.form_submit_button("Enviar Avaliação")
                    
                    if sub:
                        if not priv: st.error("Aceite a política de privacidade.")
                        elif cat == "": st.error("Escolha um Assunto.")
                        else:
                            # TENTA SALVAR NA PLANILHA
                            sucesso = salvar_feedback(nome, nota, motivo, cat)
                            if sucesso:
                                st.success("✅ Feedback salvo com sucesso no Google Sheets!")
                                st.balloons()
                st.markdown('</div>', unsafe_allow_html=True)
