import streamlit as st
import os
import json
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Prime Tech - Sistema de Gestão", 
    page_icon="💻", 
    layout="wide"
)

# --- DIRETÓRIOS E FICHEIROS DE DADOS ---
PASTA_DADOS = "dados"
if not os.path.exists(PASTA_DADOS):
    os.makedirs(PASTA_DADOS)

ARQ_CLIENTES = os.path.join(PASTA_DADOS, "clientes.json")
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
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- VALIDAÇÃO DE CPF ---
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

# --- CONTROLO DE AUTENTICAÇÃO (LOGIN) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #00ffff;'>PRIME TECH</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #b19cd9;'>SISTEMA DE GESTÃO — ACESSO</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("Digite a senha de acesso (padrão: admin123):", type="password")
        if st.button("Entrar no Sistema", use_container_width=True):
            if senha == "admin123":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
    st.stop()

# --- MENU LATERAL (SIDEBAR) ---
st.sidebar.markdown("# 🚀 PRIME TECH")
st.sidebar.markdown("### Sistema de Gestão")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegação", ["📊 Dashboard", "👥 Clientes", "💰 Financeiro", "ℹ️ Sobre o Sistema"])

if st.sidebar.button("🚪 Terminar Sessão"):
    st.session_state.autenticado = False
    st.rerun()

# --- 1. DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Executivo")
    clientes = carregar_dados(ARQ_CLIENTES)
    financeiro = carregar_dados(ARQ_FINANCEIRO)
    
    total_recebido = sum(f.get('valor_pago', 0) for f in financeiro)
    a_receber = sum(f.get('saldo_restante', 0) for f in financeiro)
    pendentes_qtd = len([f for f in financeiro if f.get('status') != "🟢 PAGO"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Clientes Registados", len(clientes))
    col2.metric("💰 Total Recebido", f"R$ {total_recebido:.2f}")
    col3.metric("🟡 A Receber", f"R$ {a_receber:.2f}")
    
    st.markdown("---")
    st.subheader("🔔 Avisos do Sistema")
    if pendentes_qtd > 0:
        st.warning(f"⚠️ Existem {pendentes_qtd} contas com pagamento pendente ou parcial.")
    else:
        st.success("✔ Nenhuma pendência financeira crítica no momento.")

# --- 2. CLIENTES ---
elif menu == "👥 Clientes":
    st.title("👥 Gestão de Clientes")
    aba1, aba2 = st.tabs(["➕ Cadastrar Novo Cliente", "🔍 Pesquisar / Listar"])
    
    clientes = carregar_dados(ARQ_CLIENTES)
    
    with aba1:
        st.subheader("Registo de Novo Cliente")
        with st.form("form_cliente"):
            nome = st.text_input("Nome Completo")
            cpf_raw = st.text_input("CPF (Apenas números)")
            telefone = st.text_input("Telefone / WhatsApp")
            email = st.text_input("E-mail")
            cidade = st.text_input("Cidade / Estado")
            
            submitted = st.form_submit_button("Salvar Cliente")
            if submitted:
                if not nome.strip():
                    st.error("O nome completo é obrigatório.")
                elif not validar_cpf(cpf_raw):
                    st.error("❌ CPF inválido! Verifique os números.")
                else:
                    cpf_formatado = formatar_cpf(cpf_raw)
                    if any(c['cpf'] == cpf_formatado for c in clientes):
                        st.warning("⚠️ Este CPF já pertence a outro cliente cadastrado.")
                    else:
                        novo_c = {
                            "id": len(clientes) + 1,
                            "nome": nome.strip(),
                            "cpf": cpf_formatado,
                            "telefone": telefone.strip(),
                            "email": email.strip(),
                            "cidade": cidade.strip(),
                            "data_cadastro": datetime.now().strftime("%d/%m/%Y")
                        }
                        clientes.append(novo_c)
                        salvar_dados(ARQ_CLIENTES, clientes)
                        st.success("✔ Cliente cadastrado com sucesso!")

    with aba2:
        st.subheader("Pesquisa de Clientes")
        termo = st.text_input("Digite parte do nome ou CPF para pesquisar:").lower().strip()
        
        encontrados = [c for c in clientes if termo in c['nome'].lower() or termo in c['cpf']] if termo else clientes
        
        if encontrados:
            st.write(f"Mostrando {len(encontrados)} cliente(s):")
            for c in encontrados:
                st.info(f"**{c['nome']}**\n\n🆔 CPF: `{c['cpf']}` | 📞 Tel: {c['telefone']} | 📧 E-mail: {c['email']} | 🏙️ Cidade: {c['cidade']}")
        else:
            st.warning("Nenhum cliente encontrado.")

# --- 3. FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.title("💰 Controlo Financeiro")
    aba_fin1, aba_fin2 = st.tabs(["➕ Registar Conta / Serviço", "💵 Listar e Dar Baixa"])
    
    financeiro = carregar_dados(ARQ_FINANCEIRO)
    
    with aba_fin1:
        st.subheader("Novo Registo Financeiro")
        with st.form("form_fin"):
            cli = st.text_input("Nome do Cliente")
            desc = st.text_input("Descrição do Serviço ou Produto")
            val = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
            
            sub_fin = st.form_submit_button("Registar Conta")
            if sub_fin:
                if not cli or not desc or val <= 0:
                    st.error("Preencha todos os campos corretamente.")
                else:
                    reg = {
                        "id": len(financeiro) + 1,
                        "cliente": cli.strip(),
                        "descricao": desc.strip(),
                        "valor_total": val,
                        "valor_pago": 0.0,
                        "saldo_restante": val,
                        "status": "🔴 PENDENTE",
                        "data": datetime.now().strftime("%d/%m/%Y")
                    }
                    financeiro.append(reg)
                    salvar_dados(ARQ_FINANCEIRO, financeiro)
                    st.success("✔ Registo financeiro criado com sucesso!")

    with aba_fin2:
        st.subheader("Contas e Status de Pagamento")
        if financeiro:
            for f in financeiro:
                st.markdown(f"**ID: {f['id']}** | **{f['cliente']}** — {f['descricao']} | Total: R$ {f['valor_total']:.2f} | Pago: R$ {f['valor_pago']:.2f} | Restante: R$ {f['saldo_restante']:.2f} | **{f['status']}**")
            
            st.markdown("---")
            st.subheader("Registar Baixa / Pagamento Parcial ou Total")
            reg_id = st.number_input("Digite o ID do registo:", min_value=1, step=1)
            val_pag = st.number_input("Valor a pagar agora (R$):", min_value=0.0, format="%.2f")
            
            if st.button("Confirmar Pagamento"):
                alvo = next((item for item in financeiro if item['id'] == reg_id), None)
                if not alvo:
                    st.error("❌ Registo não encontrado.")
                elif val_pag > alvo['saldo_restante']:
                    st.error("❌ O valor do pagamento não pode ser maior que o saldo restante.")
                else:
                    alvo['valor_pago'] += val_pag
                    alvo['saldo_restante'] = alvo['valor_total'] - alvo['valor_pago']
                    
                    if alvo['saldo_restante'] == 0:
                        alvo['status'] = "🟢 PAGO"
                    elif alvo['valor_pago'] > 0:
                        alvo['status'] = "🟡 PARCIAL"
                    else:
                        alvo['status'] = "🔴 PENDENTE"
                        
                    salvar_dados(ARQ_FINANCEIRO, financeiro)
                    st.success(f"✔ Pagamento registrado com sucesso! Novo saldo: R$ {alvo['saldo_restante']:.2f} ({alvo['status']})")
                    st.rerun()
        else:
            st.info("Nenhum registo financeiro encontrado.")

# --- 4. SOBRE O SISTEMA ---
elif menu == "ℹ️ Sobre o Sistema":
    st.title("ℹ️ Sobre o Sistema")
    st.markdown("""
    ### 🌟 PRIME TECH — SISTEMA DE GESTÃO
    * **Versão:** 1.0.0
    * **Desenvolvida por:** Daniela Reis
    * **Tecnologia:** Python, Streamlit & JSON Storage
    * **Propósito:** Aplicação comercial projetada para automação de cadastros de clientes, controlo de fluxo de caixa, validações algorítmicas e relatórios gerenciais em tempo real.
    """)
