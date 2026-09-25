import streamlit as st
import os
import json
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA E IDENTIDADE VISUAL ---
st.set_page_config(
    page_title="Prime Tech | Sistema de Gestão", 
    page_icon="💻", 
    layout="wide"
)

# Injeção de CSS customizado com o design exato da Prime Tech
st.markdown("""
<style>
    .stApp {
        background-color: #0b0c10;
        color: #ffffff;
    }
    h1, h2, h3, h4 {
        color: #00ffff !important;
    }
    p, label, span, div, .stMarkdown {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] {
        background-color: #12141a;
        border-right: 1px solid #1f2833;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        color: #0b0c10;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0, 210, 255, 0.3);
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #3a7bd5 0%, #00d2ff 100%);
        color: #ffffff;
    }
    input, textarea, select {
        background-color: #1f2833 !important;
        color: #ffffff !important;
        border: 1px solid #2c353d !important;
    }
    .logo-container {
        text-align: center;
        padding: 10px;
        background: #0b0c10;
        border-radius: 10px;
        border: 1px solid #1f2833;
        margin-bottom: 15px;
    }
    .logo-titulo {
        font-size: 22px;
        font-weight: 900;
        color: #00ffff;
        letter-spacing: 2px;
        margin: 0;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }
    .logo-sub {
        font-size: 11px;
        color: #ffffff;
        letter-spacing: 1px;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- DIRETÓRIOS E PERSISTÊNCIA (JSON) ---
PASTA_DADOS = "dados"
PASTA_BACKUP = "backups"

if not os.path.exists(PASTA_DADOS):
    os.makedirs(PASTA_DADOS)
if not os.path.exists(PASTA_BACKUP):
    os.makedirs(PASTA_BACKUP)

ARQ_CLIENTES = os.path.join(PASTA_DADOS, "clientes.json")
ARQ_ATENDIMENTOS = os.path.join(PASTA_DADOS, "atendimentos.json")
ARQ_FINANCEIRO = os.path.join(PASTA_DADOS, "financeiro.json")

def carregar_dados(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_dados(caminho, dados):
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"❌ Erro crítico ao gravar dados em {caminho}: {e}")

# --- VALIDAÇÕES ---
def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10) % 11
    if digito1 == 10: digito1 = 0
    if digito1 != int(cpf[9]): return False
    
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10) % 11
    if digito2 == 10: digito2 = 0
    if digito2 != int(cpf[10]): return False
    return True

def formatar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

# --- CONTROLO DE AUTENTICAÇÃO SEGURA (DIRETO NO CÓDIGO) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 32px; font-weight: 900; color: #00ffff; text-shadow: 0 0 15px rgba(0, 255, 255, 0.4);">PRIME TECH</div>
            <div style="font-size: 14px; color: #ffffff; letter-spacing: 2px;">SISTEMA DE GESTÃO</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Digite a senha de acesso:", type="password")
        if st.button("Entrar no Sistema", use_container_width=True):
            if senha == "13071990":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
    st.stop()

# --- MENU LATERAL (SIDEBAR COM O VISUAL DA LOGO) ---
st.sidebar.markdown("""
    <div class="logo-container">
        <div class="logo-titulo">PRIME TECH</div>
        <div style="background: linear-gradient(90deg, transparent, #00ffff, transparent); height: 2px; margin: 5px 0;"></div>
        <div class="logo-sub">SISTEMA DE GESTÃO</div>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Navegação", [
    "📊 Dashboard", 
    "👥 Clientes", 
    "🛠️ Atendimentos", 
    "💰 Financeiro", 
    "📊 Relatórios", 
    "🔔 Avisos", 
    "💾 Backup", 
    "ℹ️ Sobre o Sistema"
])

if st.sidebar.button("🚪 Terminar Sessão"):
    st.session_state.autenticado = False
    st.rerun()

# --- 1. DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Executivo")
    clientes = carregar_dados(ARQ_CLIENTES)
    atendimentos = carregar_dados(ARQ_ATENDIMENTOS)
    financeiro = carregar_dados(ARQ_FINANCEIRO)
    
    total_recebido = sum(f.get('valor_pago', 0) for f in financeiro)
    a_receber = sum(f.get('saldo_restante', 0) for f in financeiro)
    pendentes_qtd = len([f for f in financeiro if f.get('status') != "🟢 PAGO"])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Clientes", len(clientes))
    col2.metric("🛠️ Atendimentos", len(atendimentos))
    col3.metric("💰 Total Recebido", f"R$ {total_recebido:.2f}")
    col4.metric("🟡 A Receber", f"R$ {a_receber:.2f}")
    
    st.markdown("---")
    st.subheader("🔔 Avisos Rápidos")
    if pendentes_qtd > 0:
        st.warning(f"⚠️ Existem {pendentes_qtd} contas com pagamento pendente ou parcial.")
    else:
        st.success("✔ Nenhuma pendência financeira crítica no momento.")

# --- 2. CLIENTES ---
elif menu == "👥 Clientes":
    st.title("👥 Gestão de Clientes")
    aba1, aba2, aba3 = st.tabs(["➕ Cadastrar Novo", "🔍 Pesquisar & Listar", "📇 Ficha Completa"])
    
    clientes = carregar_dados(ARQ_CLIENTES)
    
    with aba1:
        st.subheader("Registo de Novo Cliente")
        with st.form("form_cliente"):
            nome = st.text_input("Nome Completo *")
            cpf_raw = st.text_input("CPF (Apenas números ou formatado) *")
            nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA)")
            telefone = st.text_input("Telefone / WhatsApp *")
            email = st.text_input("E-mail")
            endereco = st.text_input("Endereço e Número")
            cidade = st.text_input("Cidade / Estado *")
            observacoes = st.text_area("Observações")
            
            submitted = st.form_submit_button("Salvar Cliente")
            if submitted:
                if not nome.strip() or not cpf_raw.strip():
                    st.error("❌ Nome e CPF são obrigatórios.")
                elif not validar_cpf(cpf_raw):
                    st.error("❌ CPF inválido! Verifique os dígitos informados.")
                else:
                    cpf_formatado = formatar_cpf(cpf_raw)
                    if any(c['cpf'] == cpf_formatado for c in clientes):
                        cli_existente = next(c for c in clientes if c['cpf'] == cpf_formatado)
                        st.warning(f"⚠️ Este CPF já pertence ao cliente: {cli_existente['nome']}")
                    else:
                        novo_id = max([c.get('id', 0) for c in clientes], default=0) + 1
                        novo_c = {
                            "id": novo_id,
                            "nome": nome.strip(),
                            "cpf": cpf_formatado,
                            "nascimento": nascimento.strip(),
                            "telefone": telefone.strip(),
                            "email": email.strip(),
                            "endereco": endereco.strip(),
                            "cidade": cidade.strip(),
                            "observacoes": observacoes.strip(),
                            "data_cadastro": datetime.now().strftime("%d/%m/%Y"),
                            "status": "🟢 ATIVO"
                        }
                        clientes.append(novo_c)
                        salvar_dados(ARQ_CLIENTES, clientes)
                        st.success("✔ Cliente cadastrado com sucesso!")

    with aba2:
        st.subheader("Pesquisa Inteligente de Clientes")
        termo = st.text_input("Digite parte do nome, CPF ou telefone:").lower().strip()
        encontrados = [c for c in clientes if termo in c['nome'].lower() or termo in c['cpf'] or termo in c['telefone']] if termo else clientes
        
        if encontrados:
            st.write(f"Resultados encontrados ({len(encontrados)}):")
            for c in encontrados:
                st.info(f"**ID: {c['id']}** | **{c['nome']}** | CPF: `{c['cpf']}` | Tel: {c['telefone']} | Cidade: {c['cidade']}")
        else:
            st.warning("Nenhum cliente encontrado.")

    with aba3:
        st.subheader("Ficha Completa e Gestão do Cliente")
        if clientes:
            cliente_nomes = [f"{c['id']} - {c['nome']} ({c['cpf']})" for c in clientes]
            escolha = st.selectbox("Selecione o Cliente:", cliente_nomes)
            cli_id = int(escolha.split(" - ")[0])
            cli_obj = next(c for c in clientes if c['id'] == cli_id)
            
            financeiro = carregar_dados(ARQ_FINANCEIRO)
            compras_cli = [f for f in financeiro if f.get('cliente_id') == cli_id or f['cliente'].lower() == cli_obj['nome'].lower()]
            total_comprado = sum(f['valor_total'] for f in compras_cli)
            total_pago = sum(f['valor_pago'] for f in compras_cli)
            debito = sum(f['saldo_restante'] for f in compras_cli)
            
            st.markdown(f"""
            ### ╔════════════════════════════════════════╗
            ### ║ FICHA DO CLIENTE: {cli_obj['nome']}
            ### ╠════════════════════════════════════════╣
            * **CPF:** `{cli_obj['cpf']}`
            * **Telefone:** {cli_obj['telefone']}
            * **E-mail:** {cli_obj['email']}
            * **Cidade:** {cli_obj['cidade']}
            * **Data de Cadastro:** {cli_obj['data_cadastro']}
            * **Total Comprado:** R$ {total_comprado:.2f}
            * **Total Pago:** R$ {total_pago:.2f}
            * **Débito Atual:** R$ {debito:.2f}
            ### ╚════════════════════════════════════════╝
            """)
            
            if st.button("Excluir Cliente"):
                clientes = [c for c in clientes if c['id'] != cli_id]
                salvar_dados(ARQ_CLIENTES, clientes)
                st.success("✔ Cliente excluído com sucesso!")
                st.rerun()
        else:
            st.info("Nenhum cliente registado para exibir ficha.")

# --- 3. ATENDIMENTOS ---
elif menu == "🛠️ Atendimentos":
    st.title("🛠️ Gestão de Atendimentos")
    atendimentos = carregar_dados(ARQ_ATENDIMENTOS)
    clientes = carregar_dados(ARQ_CLIENTES)
    
    aba_at1, aba_at2 = st.tabs(["➕ Registar Atendimento", "📋 Listar Histórico"])
    
    with aba_at1:
        if not clientes:
            st.warning("Cadastre clientes primeiro para vincular atendimentos.")
        else:
            with st.form("form_atend"):
                cliente_opcoes = {f"{c['nome']} (ID: {c['id']})": c for c in clientes}
                cli_escolhido_str = st.selectbox("Cliente", list(cliente_opcoes.keys()))
                cli_obj = cliente_opcoes[cli_escolhido_str]
                
                servico = st.text_input("Serviço ou Produto")
                descricao = st.text_area("Descrição detalhada")
                valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
                pagamento_forma = st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito", "Dinheiro", "Boleto", "A Prazo"])
                status_atend = st.selectbox("Status", ["Concluído", "Em Andamento", "Agendado"])
                
                if st.form_submit_button("Registar Atendimento"):
                    novo_at_id = max([a.get('id', 0) for a in atendimentos], default=0) + 1
                    novo_at = {
                        "id": novo_at_id,
                        "cliente_id": cli_obj['id'],
                        "cliente": cli_obj['nome'],
                        "servico": servico.strip(),
                        "descricao": descricao.strip(),
                        "valor": valor,
                        "forma_pagamento": pagamento_forma,
                        "status": status_atend,
                        "data": datetime.now().strftime("%d/%m/%Y")
                    }
                    atendimentos.append(novo_at)
                    salvar_dados(ARQ_ATENDIMENTOS, atendimentos)
                    
                    financeiro = carregar_dados(ARQ_FINANCEIRO)
                    novo_fin_id = max([f.get('id', 0) for f in financeiro], default=0) + 1
                    novo_fin = {
                        "id": novo_fin_id,
                        "cliente_id": cli_obj['id'],
                        "cliente": cli_obj['nome'],
                        "descricao": f"Atendimento #{novo_at['id']} - {servico}",
                        "valor_total": valor,
                        "valor_pago": valor if pagamento_forma != "A Prazo" else 0.0,
                        "saldo_restante": 0.0 if pagamento_forma != "A Prazo" else valor,
                        "status": "🟢 PAGO" if pagamento_forma != "A Prazo" else "🔴 PENDENTE",
                        "data": datetime.now().strftime("%d/%m/%Y")
                    }
                    financeiro.append(novo_fin)
                    salvar_dados(ARQ_FINANCEIRO, financeiro)
                    st.success("✔ Atendimento registado e integrado ao financeiro com sucesso!")

    with aba_at2:
        st.subheader("Histórico de Atendimentos")
        if atendimentos:
            for at in atendimentos:
                st.info(f"**Atendimento #{at['id']}** | Cliente: **{at['cliente']}** | Serviço: {at['servico']} | Valor: R$ {at['valor']:.2f} | Data: {at['data']} | Status: {at['status']}")
        else:
            st.info("Nenhum atendimento registado.")

# --- 4. FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.title("💰 Controlo Financeiro & Pagamentos")
    financeiro = carregar_dados(ARQ_FINANCEIRO)
    
    aba_fin1, aba_fin2 = st.tabs(["💵 Contas e Baixas", "➕ Lançamento Manual"])
    
    with aba_fin1:
        st.subheader("Contas a Receber e Status")
        if financeiro:
            for f in financeiro:
                st.markdown(f"**ID: {f['id']}** | **{f['cliente']}** — {f['descricao']} | Total: R$ {f['valor_total']:.2f} | Pago: R$ {f['valor_pago']:.2f} | Restante: R$ {f['saldo_restante']:.2f} | **{f['status']}**")
            
            st.markdown("---")
            st.subheader("Registar Pagamento (Baixa Parcial ou Total)")
            reg_id = st.number_input("Digite o ID da conta:", min_value=1, step=1)
            valor_pagamento = st.number_input("Valor pago agora (R$):", min_value=0.0, format="%.2f")
            
            if st.button("Confirmar Baixa de Pagamento"):
                alvo = next((item for item in financeiro if item['id'] == reg_id), None)
                if not alvo:
                    st.error("❌ Registo financeiro não encontrado.")
                elif valor_pagamento > alvo['saldo_restante']:
                    st.error("❌ O valor do pagamento excede o saldo restante em dívida.")
                else:
                    alvo['valor_pago'] += valor_pagamento
                    alvo['saldo_restante'] = alvo['valor_total'] - alvo['valor_pago']
                    
                    if alvo['saldo_restante'] == 0:
                        alvo['status'] = "🟢 PAGO"
                    elif alvo['valor_pago'] > 0:
                        alvo['status'] = "🟡 PARCIAL"
                    else:
                        alvo['status'] = "🔴 PENDENTE"
                        
                    salvar_dados(ARQ_FINANCEIRO, financeiro)
                    st.success(f"✔ Pagamento registado! Restante atualizado: R$ {alvo['saldo_restante']:.2f} ({alvo['status']})")
                    st.rerun()
        else:
            st.info("Nenhum registo financeiro encontrado.")

    with aba_fin2:
        st.subheader("Novo Lançamento Financeiro Manual")
        with st.form("form_fin_manual"):
            cli = st.text_input("Nome do Cliente")
            desc = st.text_input("Descrição")
            val = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Adicionar Lançamento"):
                if not cli or val <= 0:
                    st.error("Preencha os campos corretamente.")
                else:
                    novo_fin_id = max([f.get('id', 0) for f in financeiro], default=0) + 1
                    novo_f = {
                        "id": novo_fin_id,
                        "cliente": cli.strip(),
                        "descricao": desc.strip(),
                        "valor_total": val,
                        "valor_pago": 0.0,
                        "saldo_restante": val,
                        "status": "🔴 PENDENTE",
                        "data": datetime.now().strftime("%d/%m/%Y")
                    }
                    financeiro.append(novo_f)
                    salvar_dados(ARQ_FINANCEIRO, financeiro)
                    st.success("✔ Registo financeiro criado com sucesso!")

# --- 5. RELATÓRIOS ---
elif menu == "📊 Relatórios":
    st.title("📊 Relatórios Gerenciais")
    financeiro = carregar_dados(ARQ_FINANCEIRO)
    clientes = carregar_dados(ARQ_CLIENTES)
    
    tipo_rel = st.selectbox("Selecione o Relatório", [
        "Relatório Financeiro Geral", 
        "Clientes Devedores (Inadimplentes)", 
        "Listagem Geral de Clientes"
    ])
    
    if tipo_rel == "Relatório Financeiro Geral":
        st.subheader("RELATÓRIO FINANCEIRO")
        total_geral = sum(f['valor_total'] for f in financeiro)
        total_recebido = sum(f['valor_pago'] for f in financeiro)
        total_aberto = sum(f['saldo_restante'] for f in financeiro)
        st.info(f"💰 Faturamento Total: R$ {total_geral:.2f}\n\n🟢 Total Recebido: R$ {total_recebido:.2f}\n\n🔴 Em Aberto: R$ {total_aberto:.2f}")
        
    elif tipo_rel == "Clientes Devedores (Inadimplentes)":
        st.subheader("CLIENTES COM DÉBITOS PENDENTES")
        devedores = [f for f in financeiro if f['saldo_restante'] > 0]
        if devedores:
            for d in devedores:
                st.warning(f"⚠️ **{d['cliente']}** — Dívida: R$ {d['saldo_restante']:.2f} ({d['descricao']})")
        else:
            st.success("✔ Nenhum cliente inadimplente no momento.")
            
    elif tipo_rel == "Listagem Geral de Clientes":
        st.subheader("LISTA DE CLIENTES CADASTRADOS")
        if clientes:
            for c in clientes:
                st.write(f"- **{c['nome']}** | CPF: `{c['cpf']}` | Tel: {c['telefone']}")
        else:
            st.info("Nenhum cliente cadastrado.")

# --- 6. AVISOS ---
elif menu == "🔔 Avisos":
    st.title("🔔 Avisos Automáticos do Sistema")
    financeiro = carregar_dados(ARQ_FINANCEIRO)
    atendimentos = carregar_dados(ARQ_ATENDIMENTOS)
    
    pendentes = [f for f in financeiro if f['status'] != "🟢 PAGO"]
    
    st.markdown("### 🔔 Central de Alertas")
    if pendentes:
        st.warning(f"⚠️ Existem {len(pendentes)} contas com pagamento pendente ou parcial.")
    else:
        st.success("✔ Nenhuma pendência financeira.")
        
    st.info(f"📅 Total de atendimentos registados no sistema: {len(atendimentos)}")

# --- 7. BACKUP ---
elif menu == "💾 Backup":
    st.title("💾 Gestão de Backup e Restauração")
    if st.button("Criar Novo Backup dos Dados"):
        data_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        caminho_bkp = os.path.join(PASTA_BACKUP, f"backup_{data_str}.json")
        
        dados_geral = {
            "clientes": carregar_dados(ARQ_CLIENTES),
            "atendimentos": carregar_dados(ARQ_ATENDIMENTOS),
            "financeiro": carregar_dados(ARQ_FINANCEIRO)
        }
        
        with open(caminho_bkp, "w", encoding="utf-8") as f:
            json.dump(dados_geral, f, ensure_ascii=False, indent=4)
        st.success(f"✔ Backup criado com sucesso na pasta backups/ ({caminho_bkp})!")
        
    st.subheader("Histórico de Backups Disponíveis")
    if os.path.exists(PASTA_BACKUP):
        arquivos_bkp = os.listdir(PASTA_BACKUP)
        if arquivos_bkp:
            for bkp in arquivos_bkp:
                st.text(f"📁 {bkp}")
        else:
            st.info("Nenhum backup encontrado.")

# --- 8. SOBRE O SISTEMA ---
elif menu == "ℹ️ Sobre o Sistema":
    st.title("ℹ️ Sobre o Sistema")
    st.markdown("""
    ### 🌟 PRIME TECH SOLUTIONS — SISTEMA DE GESTÃO
    * **Versão:** 1.1.2 (Direct Secure)
    * **Desenvolvida por:** Daniela Reis
    * **Tecnologia:** Python, Streamlit & JSON Storage
    * **Propósito:** Aplicação comercial projetada para automação de cadastros de clientes, controlo de fluxo de caixa, validações algorítmicas, histórico, relatórios e mecanismos de backup seguro.
    """)
