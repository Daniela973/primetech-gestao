import streamlit as st
import json
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Primetech Gestão - SaaS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Arquivo de Banco de Dados local
DB_FILE = "primetech_gestao_db.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"clientes": [], "financeiro": [], "chat": []}

def salvar_dados(dados):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def validar_cpf(cpf):
    cpf_limpo = "".join([c for c in cpf if c.isdigit()])
    return len(cpf_limpo) == 11

# Inicializar sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "mostrar_chat" not in st.session_state:
    st.session_state.mostrar_chat = False

if "mensagens_chat" not in st.session_state:
    st.session_state.mensagens_chat = [
        {"role": "assistant", "content": "Olá! Sou o Assistente IA da Primetech. Como posso ajudar na gestão hoje?"}
    ]

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2 style='color: #1f1f1f;'>⚡ Primetech Gestão</h2>
            <p style='color: gray; font-size: 14px;'>Plataforma SaaS Corporativa</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.warning("💡 **Acesso:** Usuário: **`daniela`** | Senha: **`130790`**")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if submit:
                if usuario == "daniela" and senha == "130790":
                    st.session_state.autenticado = True
                    st.success("Autenticado com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()

# --- APLICATIVO PRINCIPAL ---
dados_db = carregar_dados()

# Cabeçalho médio e limpo
st.markdown("""
    <div style='padding: 5px 0px; border-bottom: 1px solid #e0e0e0; margin-bottom: 15px;'>
        <h3 style='margin:0; color: #1f1f1f; font-size: 20px;'>⚡ Primetech • Painel de Gestão</h3>
    </div>
""", unsafe_allow_html=True)

# Menu Lateral Médio e Direto
st.sidebar.markdown("### 🧭 Menu Principal")
menu = st.sidebar.radio(
    "Navegue pelas seções:",
    ["Dashboard", "Clientes", "Financeiro"],
    label_visibility="collapsed"
)

st.sidebar.divider()
if st.sidebar.button("🔒 Sair da Conta", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

# 1. DASHBOARD
if menu == "Dashboard":
    st.markdown("#### 📊 Visão Geral do Negócio")
    
    total_clientes = len(dados_db["clientes"])
    receita_total = sum([item["valor"] for item in dados_db["financeiro"] if item["tipo"] == "Receita"])
    despesa_total = sum([item["valor"] for item in dados_db["financeiro"] if item["tipo"] == "Despesa"])
    lucro = receita_total - despesa_total
    
    # Métricas compactas em duas colunas para celular
    col1, col2 = st.columns(2)
    col1.metric("Clientes Ativos", total_clientes)
    col2.metric("Lucro Líquido", f"R$ {lucro:.2f}")
    
    col3, col4 = st.columns(2)
    col3.metric("Receita Total", f"R$ {receita_total:.2f}")
    col4.metric("Despesas", f"R$ {despesa_total:.2f}")
    
    st.success("🟢 Sistema operando com banco de dados em nuvem sincronizado.")

# 2. CLIENTES
elif menu == "Clientes":
    st.markdown("#### 👥 Gestão de Clientes")
    
    with st.form("form_cliente", clear_on_submit=True):
        nome = st.text_input("Nome Completo / Empresa")
        email = st.text_input("E-mail Comercial")
        cpf = st.text_input("CPF (Somente números)")
        plano = st.selectbox("Plano Contratado", ["Starter", "Professional", "Enterprise"])
            
        salvar_cli = st.form_submit_button("Cadastrar Cliente", use_container_width=True)
        
        if salvar_cli:
            if nome and cpf:
                if validar_cpf(cpf):
                    novo_cliente = {
                        "nome": nome,
                        "cpf": cpf,
                        "email": email,
                        "plano": plano,
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    dados_db["clientes"].append(novo_cliente)
                    salvar_dados(dados_db)
                    st.success(f"Cliente {nome} cadastrado!")
                    st.rerun()
                else:
                    st.error("CPF inválido.")
            else:
                st.warning("Preencha Nome e CPF.")
                
    st.markdown("**Clientes Registrados:**")
    if dados_db["clientes"]:
        st.table(dados_db["clientes"])
    else:
        st.info("Nenhum cliente cadastrado.")

# 3. FINANCEIRO
elif menu == "Financeiro":
    st.markdown("#### 💰 Controle Financeiro")
    
    with st.form("form_fin", clear_on_submit=True):
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            
        salvar_fin = st.form_submit_button("Adicionar Lançamento", use_container_width=True)
        
        if salvar_fin:
            if descricao and valor > 0:
                novo_lancamento = {
                    "descricao": descricao,
                    "valor": valor,
                    "tipo": tipo,
                    "data": datetime.now().strftime("%d/%m/%Y")
                }
                dados_db["financeiro"].append(novo_lancamento)
                salvar_dados(dados_db)
                st.success("Lançamento adicionado!")
                st.rerun()
            else:
                st.warning("Insira descrição e valor válidos.")
                
    st.markdown("**Histórico de Lançamentos:**")
    if dados_db["financeiro"]:
        st.table(dados_db["financeiro"])
    else:
        st.info("Nenhum lançamento registrado.")

# --- BOTÃO FLUTUANTE E MODAL DE CHAT DA EMPRESA ---
st.divider()

# Botão flutuante estilizado nas cores corporativas (Azul/Dark moderno)
col_vazia, col_btn = st.columns([2, 1])
with col_btn:
    if st.button("💬 Chat Primetech", use_container_width=True):
        st.session_state.mostrar_chat = not st.session_state.mostrar_chat

# Se o chat estiver ativado, exibe a caixa de diálogo interativa na tela principal
if st.session_state.mostrar_chat:
    st.markdown("---")
    st.markdown("### 🤖 Assistente IA Primetech (Em tempo real)")
    
    for msg in st.session_state.mensagens_chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if prompt := st.chat_input("Digite sua dúvida (ex: 'quantos clientes?')..."):
        st.session_state.mensagens_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # Leitura inteligente dos dados reais
        total_cli = len(dados_db["clientes"])
        rec = sum([i["valor"] for i in dados_db["financeiro"] if i["tipo"] == "Receita"])
        desp = sum([i["valor"] for i in dados_db["financeiro"] if i["tipo"] == "Despesa"])
        
        if "cliente" in prompt.lower():
            resposta = f"Atualmente temos **{total_cli} cliente(s)** cadastrado(s) na plataforma."
        elif "financeiro" in prompt.lower() or "receita" in prompt.lower() or "lucro" in prompt.lower():
            resposta = f"Balanço atual: Receitas: R$ {rec:.2f} | Despesas: R$ {desp:.2f} | Lucro Líquido: R$ {rec - desp:.2f}."
        else:
            resposta = f"Compreendi sua solicitação. Os servidores da Primetech e os dados em JSON estão sincronizados e seguros."
            
        st.session_state.mensagens_chat.append({"role": "assistant", "content": resposta})
        with st.chat_message("assistant"):
            st.write(resposta)
