import streamlit as st
import json
import os
from datetime import datetime

# Configuração da página e identidade visual
st.set_page_config(
    page_title="Primetech Gestão - Plataforma SaaS",
    page_icon="⚡",
    layout="wide"
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

if "mensagens_chat" not in st.session_state:
    st.session_state.mensagens_chat = [
        {"role": "assistant", "content": "Olá! Sou o Assistente IA da Primetech. Estou conectado ao seu banco de dados e pronto para responder sobre clientes, finanças e gestão. Como posso ajudar?"}
    ]

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("""
        <div style='text-align: center; padding: 25px;'>
            <h1 style='color: #0e1117;'>⚡ Primetech Gestão</h1>
            <p style='color: gray; font-size: 16px;'>Plataforma Corporativa de Alta Performance</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.warning("💡 **Acesso de Demonstração:** Usuário: **`daniela`** | Senha: **`130790`**")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if submit:
                if usuario == "admin" and senha == "primetchec":
                    st.session_state.autenticado = True
                    st.success("Autenticado com sucesso! Carregando painel...")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()

# --- APLICATIVO PRINCIPAL ---
dados_db = carregar_dados()

# Topo corporativo limpo (sem foguete)
st.markdown("""
    <div style='padding: 10px 0px; border-bottom: 2px solid #f0f2f6; margin-bottom: 20px;'>
        <h2 style='margin:0; color: #1f1f1f;'>⚡ Primetech • Painel Executivo SaaS</h2>
        <p style='margin:0; color: gray; font-size: 14px;'>Ambiente seguro e integrado em nuvem</p>
    </div>
""", unsafe_allow_html=True)

# Abas superiores com resposta de clique garantida
menu = st.tabs([
    "📊 Dashboard", 
    "👥 Clientes", 
    "💰 Financeiro", 
    "💬 Chat IA Inteligente", 
    "🔒 Sair"
])

# 1. DASHBOARD
with menu[0]:
    st.subheader("Visão Geral do Negócio")
    
    total_clientes = len(dados_db["clientes"])
    receita_total = sum([item["valor"] for item in dados_db["financeiro"] if item["tipo"] == "Receita"])
    despesa_total = sum([item["valor"] for item in dados_db["financeiro"] if item["tipo"] == "Despesa"])
    lucro = receita_total - despesa_total
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clientes Ativos", total_clientes)
    col2.metric("Receita Total", f"R$ {receita_total:.2f}")
    col3.metric("Despesas", f"R$ {despesa_total:.2f}")
    col4.metric("Lucro Líquido", f"R$ {lucro:.2f}")
    
    st.info("💡 **Dica de Portfólio:** Este sistema utiliza persistência em JSON e validações ativas em tempo real, ideal para apresentação comercial.")

# 2. CLIENTES
with menu[1]:
    st.subheader("Gestão de Base de Clientes")
    
    with st.form("form_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo / Empresa")
            email = st.text_input("E-mail Comercial")
        with col2:
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
                    st.success(f"Cliente {nome} cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("CPF inválido! Verifique os dígitos.")
            else:
                st.warning("Preencha ao menos Nome e CPF.")
                
    st.markdown("### Clientes Registrados")
    if dados_db["clientes"]:
        st.table(dados_db["clientes"])
    else:
        st.info("Nenhum cliente cadastrado até o momento.")

# 3. FINANCEIRO
with menu[2]:
    st.subheader("Controle Financeiro e Caixa")
    
    with st.form("form_fin", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            descricao = st.text_input("Descrição do Lançamento")
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        with col3:
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            
        salvar_fin = st.form_submit_button("Registrar Lançamento", use_container_width=True)
        
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
                st.success("Lançamento adicionado com sucesso!")
                st.rerun()
            else:
                st.warning("Informe uma descrição e um valor válido.")
                
    st.markdown("### Histórico de Transações")
    if dados_db["financeiro"]:
        st.table(dados_db["financeiro"])
    else:
        st.info("Nenhum lançamento registrado.")

# 4. CHAT IA INTELIGENTE (Conectado aos dados reais!)
with menu[3]:
    st.subheader("💬 Assistente IA Corporativo Primetech")
    st.markdown("Converse com o assistente inteligente do sistema. Ele analisa os dados reais do seu negócio em tempo real.")
    
    # Exibir mensagens do histórico
    for msg in st.session_state.mensagens_chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Entrada de prompt interativo
    if prompt := st.chat_input("Faça uma pergunta ao assistente (ex: 'Quantos clientes temos?')..."):
        st.session_state.mensagens_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # Lógica inteligente baseada nos dados reais do sistema
        prompt_lower = prompt.lower()
        total_cli = len(dados_db["clientes"])
        rec = sum([i["valor"] for i in dados_db["financeiro"] if i["tipo"] == "Receita"])
        desp = sum([i["valor"] for i in dados_db["financeiro"] if i["tipo"] == "Despesa"])
        
        if "cliente" in prompt_lower:
            resposta_ia = f"Atualmente, o sistema possui **{total_cli} cliente(s)** cadastrado(s) na base de dados."
        elif "financeiro" in prompt_lower or "receita" in prompt_lower or "dinheiro" in prompt_lower or "caixa" in prompt_lower:
            resposta_ia = f"Análise financeira atual: Temos **R$ {rec:.2f}** em receitas registradas e **R$ {desp:.2f}** em despesas, gerando um lucro líquido de **R$ {rec - desp:.2f}**."
        elif "olá" in prompt_lower or "tudo bem" in prompt_lower:
            resposta_ia = "Olá! Tudo ótimo por aqui com os servidores da Primetech. Como posso auxiliar na sua gestão hoje?"
        else:
            resposta_ia = f"Compreendi sua dúvida sobre '{prompt}'. Como o sistema Primetech está ativo e sincronizado, todos os módulos operacionais estão seguros. Posso ajudar com mais alguma consulta aos dados?"
            
        st.session_state.mensagens_chat.append({"role": "assistant", "content": resposta_ia})
        with st.chat_message("assistant"):
            st.write(resposta_ia)

# 5. SAIR
with menu[4]:
    st.subheader("Encerrar Sessão")
    st.write("Deseja desconectar sua conta administrativa com segurança?")
    if st.button("Fazer Logout Agora", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
