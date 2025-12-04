import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Central de Experiência",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ASSETS (AQUI ESTÃO O ROBÔ E A IMAGEM) ---
# Imagem Hero (Tecnologia/Atendimento - Link Estável)
HERO_IMAGE_URL = "https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=2070&auto=format&fit=crop"

# Ícones SVG (O Robozinho que você pediu)
# Robô Azul
BOT_AVATAR_URL = "https://api.iconify.design/fluent:bot-24-filled.svg?color=%232563EB"
# Usuário Cinza
USER_AVATAR_URL = "https://api.iconify.design/solar:user-circle-bold.svg?color=%23475569"

# --- CSS "VISUAL TECH AZUL" (O DESIGN QUE VOCÊ GOSTOU) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fundo geral levemente azulado */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Esconde menu padrão */
    #MainMenu, footer, header {visibility: hidden;}

    /* HERO SECTION COM DEGRADÊ (O visual azul impactante) */
    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); /* Azul Profundo */
        padding: 4rem 2rem;
        border-radius: 0 0 24px 24px;
        color: white;
        margin-bottom: 3rem;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.2);
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 400;
        max-width: 600px;
    }

    /* CARDS FLUTUANTES */
    .content-card, div[data-testid="stMetric"], div.stDataFrame {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
    }

    /* BOTÕES COM DEGRADÊ */
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #4F46E5 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(37, 99, 235, 0.25);
    }

    /* INPUTS MODERNOS */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        border-radius: 8px;
        border: 1px solid #CBD5E1;
        padding: 10px;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    /* ABAS ESTILIZADAS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #E2E8F0;
    }
    .stTabs [aria-selected="true"] {
        color: #2563EB;
        border-bottom: 3px solid #2563EB;
    }

    /* AJUSTE PARA O ÍCONE DO ROBÔ (Para ficar transparente e bonito) */
    .stChatMessage .stChatMessageAvatar {
        background-color: transparent !important;
        width: 45px;
        height: 45px;
    }
    div[data-testid="stChatMessageContent"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
DB_FILE = 'dados_privados.db'


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, data TEXT, nome TEXT, nota INTEGER, motivo TEXT, categoria TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS config (chave TEXT PRIMARY KEY, valor TEXT)''')
    c.execute("SELECT valor FROM config WHERE chave='senha_admin'")
    if not c.fetchone(): c.execute("INSERT INTO config (chave, valor) VALUES ('senha_admin', 'admin123')")
    conn.commit()
    conn.close()


def get_senha_atual():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("SELECT valor FROM config WHERE chave='senha_admin'");
    res = c.fetchone();
    conn.close();
    return res[0] if res else 'admin123'


def alterar_senha(nova):
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("UPDATE config SET valor = ? WHERE chave='senha_admin'", (nova,));
    conn.commit();
    conn.close()


def salvar_feedback(nome, nota, motivo, categoria):
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M");
    if not nome: nome = "Anônimo"; c.execute(
        "INSERT INTO feedback (data, nome, nota, motivo, categoria) VALUES (?, ?, ?, ?, ?)",
        (data_hora, nome, nota, motivo, categoria)); conn.commit(); conn.close()


init_db()

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


# --- APP ---
query_params = st.query_params
modo_admin = query_params.get("acesso") == "admin"

if modo_admin:
    # === ADMIN ===
    st.markdown("### 🔒 Gestão Interna")
    if 'logado' not in st.session_state: st.session_state['logado'] = False

    if not st.session_state['logado']:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.info("Área Restrita")
            senha = st.text_input("Senha Mestra", type="password")
            if st.button("Acessar"):
                if senha == get_senha_atual():
                    st.session_state['logado'] = True; st.rerun()
                else:
                    st.error("Senha inválida.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # DASHBOARD
        tab1, tab2 = st.tabs(["Dashboard", "Configurações"])
        with tab1:
            conn = sqlite3.connect(DB_FILE);
            df = pd.read_sql_query("SELECT * FROM feedback ORDER BY id DESC", conn);
            conn.close()
            if not df.empty:
                total = len(df);
                promotores = len(df[df['nota'] >= 9]);
                detratores = len(df[df['nota'] <= 6]);
                nps = int(((promotores - detratores) / total) * 100) if total > 0 else 0

                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Total", total);
                k2.metric("Média", f"{df['nota'].mean():.1f}");
                k3.metric("NPS", nps);
                k4.metric("Último", df['data'].iloc[0].split()[1])
                st.write("")
                g1, g2 = st.columns(2)
                with g1:
                    st.markdown("##### Motivos"); st.bar_chart(df['categoria'].value_counts(), color="#3B82F6")
                with g2:
                    st.markdown("##### Notas"); st.line_chart(df['nota'], color="#6366F1")
                st.dataframe(df, hide_index=True, use_container_width=True,
                             column_config={"nota": st.column_config.NumberColumn("Nota", format="%d ⭐")})
                st.download_button("Baixar CSV", df.to_csv(index=False), "dados.csv")
            else:
                st.info("Aguardando dados.")
        with tab2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            n1 = st.text_input("Nova senha", type="password");
            n2 = st.text_input("Confirmar", type="password")
            if st.button("Salvar"):
                if n1 == n2 and n1:
                    alterar_senha(n1); st.success("Atualizado!")
                else:
                    st.error("Erro.")
            if st.button("Sair"): st.session_state['logado'] = False; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # === CLIENTE (O DESIGN AZUL QUE VOCÊ GOSTOU) ===

    # HERO SECTION (Azul Degradê)
    st.markdown(f"""
        <div class="hero-container">
            <div style="display: flex; align-items: center; justify-content: space-between; max-width: 1200px; margin: 0 auto; gap: 2rem;">
                <div style="flex: 1;">
                    <h1 class="hero-title">Central de <br>Sucesso do Cliente</h1>
                    <p class="hero-subtitle">
                        Canal oficial de comunicação. Tire dúvidas com nossa IA ou deixe seu feedback para a diretoria.
                    </p>
                </div>
                <div style="flex: 1; text-align: right;">
                    <img src="{HERO_IMAGE_URL}" style="border-radius: 16px; width: 100%; max-height: 300px; object-fit: cover; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # CONTEÚDO
    with st.container():
        c_l, c_main, c_r = st.columns([1, 8, 1])
        with c_main:
            tab_chat, tab_form = st.tabs(["🤖 Assistente Virtual", "⭐ Avaliar Experiência"])

            # CHAT (COM ROBOZINHO)
            with tab_chat:
                st.write("")
                if "msgs" not in st.session_state: st.session_state.msgs = [
                    {"role": "assistant", "content": "Olá! Sou a IA da empresa. Como posso ajudar?"}]

                for m in st.session_state.msgs:
                    # AQUI ESTÁ A MUDANÇA: Avatar SVG em vez de Emoji
                    avatar_icon = BOT_AVATAR_URL if m["role"] == "assistant" else USER_AVATAR_URL

                    with st.chat_message(m["role"], avatar=avatar_icon):
                        st.write(m["content"])

                if prompt := st.chat_input("Digite sua dúvida..."):
                    st.session_state.msgs.append({"role": "user", "content": prompt})
                    # Ícone do usuário na pergunta
                    with st.chat_message("user", avatar=USER_AVATAR_URL):
                        st.write(prompt)

                    time.sleep(0.4)
                    resp = responder_bot(prompt)

                    st.session_state.msgs.append({"role": "assistant", "content": resp})
                    # Ícone do robô na resposta
                    with st.chat_message("assistant", avatar=BOT_AVATAR_URL):
                        st.write(resp)

            # FORMULÁRIO (CORRIGIDO E SEM BUGS)
            with tab_form:
                st.write("")
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.subheader("Sua opinião importa")

                with st.form("feed_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        nome = st.text_input("Nome (Opcional)")
                    with c2:
                        # Dropdown Corrigido (Validação)
                        cat = st.selectbox("Assunto *", ["", "Elogio", "Sugestão", "Reclamação", "Dúvida"],
                                           format_func=lambda x: "Selecione..." if x == "" else x)

                    nota = st.slider("Nota de Satisfação", 1, 10, 10)
                    txt = st.text_area("Mensagem", placeholder="Escreva aqui...")

                    st.write("")
                    priv = st.checkbox("Concordo com a Política de Privacidade.")

                    sub = st.form_submit_button("Enviar Avaliação")

                    if sub:
                        if not priv:
                            st.error("Aceite a política de privacidade.")
                        elif cat == "":
                            st.error("Escolha um Assunto.")
                        else:
                            salvar_feedback(nome, nota, txt, cat)
                            st.success("Feedback Enviado!")
                            st.balloons()
                st.markdown('</div>', unsafe_allow_html=True)