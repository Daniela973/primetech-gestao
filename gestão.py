import datetime
import json
import os
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA (IDENTIDADE VISUAL PRIMETECH)
# ==========================================
st.set_page_config(
    page_title="Primetech Solutions - Sistema de Gestão Avançado",
    page_icon="💻",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 700; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 25px; }
    .stChatMessage { padding: 10px; border-radius: 10px; }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# FUNÇÃO DE VALIDAÇÃO DE CPF
# ==========================================


def validar_cpf(cpf):
    cpf = "".join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10) % 11
    if digito1 == 10:
        digito1 = 0
    if digito1 != int(cpf[9]):
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10) % 11
    if digito2 == 10:
        digito2 = 0
    if digito2 != int(cpf[10]):
        return False

    return True


# ==========================================
# BANCO DE DADOS LOCAL (JSON PERSISTENTE)
# ==========================================
DB_FILE = "primetech_gestao_db.json"


def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"clientes": [], "atendimentos": [], "financeiro": []}


def salvar_dados(dados):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


if "db" not in st.session_state:
    st.session_state["db"] = carregar_dados()

if "mensagens_chat" not in st.session_state:
    st.session_state["mensagens_chat"] = [
        {
            "role": "assistant",
            "content": (
                "Olá! Sou a assistente virtual da **Primetech Solutions**. Como"
                " posso te ajudar hoje?"
            ),
        }
    ]

if "chat_ativo" not in st.session_state:
    st.session_state["chat_ativo"] = False

# ==========================================
# 1. TELA DE LOGIN (SENHA CONFIGURADA AQUI)
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown(
        '<p class="main-header">PRIMETECH SOLUTIONS</p>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="sub-header">Acesso Restrito - Gestão Profissional Integrada</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        # CAMPOS DE ENTRADA DE CREDENCIAIS
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")

        if st.button("Entrar no Sistema", use_container_width=True):
            # 🔐 AQUI ESTÁ A SUA SENHA DE ADM EXPLICITAMENTE CONFIGURADA:
            if usuario_input == "admin" and senha_input == "primetchec":
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos. Tente novamente.")

        # Dica visual na tela para você lembrar fácil
        st.info(
            "💡 **Acesso Padrão Administrador:**\n* Usuário:"
            " **`daniela`**\n* Senha: **`130790`**"
        )
    st.stop()


# ==========================================
# MENU LATERAL E NAVEGAÇÃO
# ==========================================
st.sidebar.title("🚀 Primetech Gestão")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Módulos do Sistema",
    [
        "📊 Dashboard",
        "👥 Clientes",
        "🛠️ Atendimentos",
        "💰 Financeiro",
        "📈 Relatórios",
        "🔌 API",
        "🗄️ Banco de Dados",
        "⚡ Automações",
    ],
)

db = st.session_state["db"]

# Botão do Chat na Barra Lateral
st.sidebar.markdown("---")
st.sidebar.subheader("💬 Atendimento Rápido")
if st.sidebar.button(
    "🤖 Abrir Chat Primetech", use_container_width=True, type="primary"
):
    st.session_state["chat_ativo"] = not st.session_state["chat_ativo"]

# Painel do Chat Dinâmico
if st.session_state["chat_ativo"]:
    st.markdown("---")
    st.markdown("### 💬 Chat Dinâmico Primetech — Assistente Inteligente 🤖")

    for msg in st.session_state["mensagens_chat"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt_usuario := st.chat_input("Digite sua dúvida ou comando..."):
        st.session_state["mensagens_chat"].append(
            {"role": "user", "content": prompt_usuario}
        )
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        txt_lower = prompt_usuario.lower()
        if "cliente" in txt_lower:
            total_c = len(db["clientes"])
            resposta_assistente = f"Atualmente temos **{total_c} cliente(s)** cadastrado(s)."
        elif (
            "financeiro" in txt_lower
            or "receita" in txt_lower
            or "saldo" in txt_lower
        ):
            receitas = sum(
                x["valor"] for x in db["financeiro"] if x["tipo"] == "Receita"
            )
            despesas = sum(
                x["valor"] for x in db["financeiro"] if x["tipo"] == "Despesa"
            )
            saldo = receitas - despesas
            resposta_assistente = (
                f"📊 **Balanço Financeiro:** Receitas: R$ {receitas:.2f} |"
                f" Despesas: R$ {despesas:.2f} | Saldo: **R$ {saldo:.2f}**"
            )
        elif "atendimento" in txt_lower or "chamado" in txt_lower:
            total_a = len(db["atendimentos"])
            resposta_assistente = (
                f"Existem **{total_a} atendimento(s)** registrados."
            )
        else:
            resposta_assistente = (
                f"Entendi sua busca por '{prompt_usuario}'. Navegue pelos"
                " módulos ou consulte os resumos por aqui!"
            )

        st.session_state["mensagens_chat"].append(
            {"role": "assistant", "content": resposta_assistente}
        )
        with st.chat_message("assistant"):
            st.markdown(resposta_assistente)

    if st.button("❌ Fechar Chat"):
        st.session_state["chat_ativo"] = False
        st.rerun()
    st.markdown("---")

# Módulos principais (Dashboard, Clientes, Atendimentos, Financeiro, etc.)
if menu == "📊 Dashboard":
    st.markdown(
        '<p class="main-header">Dashboard Executivo</p>', unsafe_allow_html=True
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Clientes", len(db["clientes"]))
    c2.metric("Atendimentos", len(db["atendimentos"]))
    receita_total = sum(
        float(item.get("valor", 0))
        for item in db["financeiro"]
        if item.get("tipo") == "Receita"
    )
    c3.metric("Receita Consolidada", f"R$ {receita_total:.2f}")

elif menu == "👥 Clientes":
    st.markdown(
        '<p class="main-header">Gestão de Clientes</p>', unsafe_allow_html=True
    )
    with st.form("form_cliente", clear_on_submit=True):
        nome = st.text_input("Nome do Cliente / Empresa")
        cpf_input = st.text_input("CPF (Apenas números ou formatado)")
        email = st.text_input("E-mail")
        telefone = st.text_input("Telefone")
        if st.form_submit_button("Cadastrar Cliente"):
            if not nome:
                st.error("Nome obrigatório.")
            elif not validar_cpf(cpf_input):
                st.error("❌ CPF Inválido!")
            else:
                cpf_limpo = "".join(filter(str.isdigit, cpf_input))
                cpf_fmt = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
                db["clientes"].append(
                    {
                        "nome": nome,
                        "cpf": cpf_fmt,
                        "email": email,
                        "telefone": telefone,
                    }
                )
                salvar_dados(db)
                st.success("Cliente cadastrado com sucesso!")
    if db["clientes"]:
        st.dataframe(db["clientes"], use_container_width=True)

elif menu == "🛠️ Atendimentos":
    st.markdown(
        '<p class="main-header">Controle de Atendimentos</p>', unsafe_allow_html=True
    )
    if db["clientes"]:
        with st.form("form_atendimento", clear_on_submit=True):
            cliente_sel = st.selectbox(
                "Cliente", [c["nome"] for c in db["clientes"]]
            )
            descricao = st.text_area("Descrição do Chamado")
            status = st.selectbox("Status", ["Pendente", "Concluído"])
            if st.form_submit_button("Registrar"):
                db["atendimentos"].append(
                    {
                        "cliente": cliente_sel,
                        "descricao": descricao,
                        "status": status,
                        "data": str(datetime.date.today()),
                    }
                )
                salvar_dados(db)
                st.success("Registrado!")
    if db["atendimentos"]:
        st.dataframe(db["atendimentos"], use_container_width=True)

elif menu == "💰 Financeiro":
    st.markdown(
        '<p class="main-header">Módulo Financeiro</p>', unsafe_allow_html=True
    )
    with st.form("form_fin", clear_on_submit=True):
        tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Adicionar Lançamento"):
            db["financeiro"].append(
                {
                    "tipo": tipo,
                    "descricao": descricao,
                    "valor": valor,
                    "data": str(datetime.date.today()),
                }
            )
            salvar_dados(db)
            st.success("Adicionado!")
    if db["financeiro"]:
        st.dataframe(db["financeiro"], use_container_width=True)

elif menu == "📈 Relatórios":
    st.markdown(
        '<p class="main-header">Relatórios e Indicadores</p>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    col1.metric("Cadastros", len(db["clientes"]))
    col2.metric("Atendimentos", len(db["atendimentos"]))

elif menu == "🔌 API":
    st.markdown(
        '<p class="main-header">Endpoints da API</p>', unsafe_allow_html=True
    )
    st.code('{"status": "online", "versao": "2.0"}', language="json")

elif menu == "🗄️ Banco de Dados":
    st.markdown(
        '<p class="main-header">Banco de Dados Local</p>', unsafe_allow_html=True
    )
    if st.button("🔄 Resetar Banco de Dados", type="primary"):
        st.session_state["db"] = {
            "clientes": [],
            "atendimentos": [],
            "financeiro": [],
        }
        salvar_dados(st.session_state["db"])
        st.rerun()

elif menu == "⚡ Automações":
    st.markdown(
        '<p class="main-header">Central de Automações</p>', unsafe_allow_html=True
    )
    st.info("Automações operacionais configuradas.")

st.sidebar.markdown("---")
if st.sidebar.button("Sair da Sessão"):
    st.session_state["autenticado"] = False
    st.rerun()
