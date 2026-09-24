import os
import json
from datetime import datetime

# --- CORES DA IDENTIDADE VISUAL (ANSI) ---
RESET = "\033[0m"
PRETO = "\033[30m"
GRAFITE = "\033[90m"
BRANCO = "\033[97m"
CIANO = "\033[96m"
ROXO = "\033[95m"
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
NEGRITO = "\033[1m"

# --- DIRETÓRIOS E FICHEIROS DE DADOS ---
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
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def limpar_ecra():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- VALIDAÇÕES ---
def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    # Algoritmo padrão de validação de CPF
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

# --- LOGIN SIMPLES ---
def sistema_login():
    limpar_ecra()
    print(f"{CIANO}╔══════════════════════════════════════════╗{RESET}")
    print(f"{CIANO}║{RESET}         {NEGRITO}{BRANCO}PRIMETECH SOLUTIONS{RESET}              {CIANO}║{RESET}")
    print(f"{CIANO}║{RESET}         {ROXO}CONTROLO DE ACESSO{RESET}              {CIANO}║{RESET}")
    print(f"{CIANO}╚══════════════════════════════════════════╝{RESET}")
    
    senha_mestre = "admin123"
    tentativas = 3
    
    while tentativas > 0:
        senha = input(f"{BRANCO}Digite a senha de acesso (padrão: admin123): {RESET}")
        if senha == senha_mestre:
            print(f"{VERDE}✔ Acesso autorizado com sucesso!{RESET}")
            input("Pressione Enter para entrar no sistema...")
            return True
        else:
            tentativas -= 1
            print(f"{VERMELHO}✖ Senha incorreta! Tentativas restantes: {tentativas}{RESET}")
    print(f"{VERMELHO}Acesso bloqueado por segurança.{RESET}")
    return False

# --- MÓDULO CLIENTES ---
def menu_clientes():
    clientes = carregar_dados(ARQ_CLIENTES)
    while True:
        limpar_ecra()
        print(f"{CIANO}=== 👥 GESTÃO DE CLIENTES ==={RESET}")
        print("1. Cadastrar Novo Cliente")
        print("2. Pesquisar / Listar Clientes")
        print("0. Voltar ao Menu Principal")
        
        opcao = input(f"{ROXO}Escolha uma opção: {RESET}")
        
        if opcao == "1":
            print(f"\n{NEGRITO}--- NOVO CLIENTE ---{RESET}")
            nome = input("Nome completo: ").strip()
            if not nome:
                print(f"{VERMELHO}Nome não pode estar vazio!{RESET}")
                input("Pressione Enter...")
                continue
                
            cpf_raw = input("CPF (apenas números ou formatado): ").strip()
            if not validar_cpf(cpf_raw):
                print(f"{VERMELHO}❌ CPF inválido! Cadastro cancelado.{RESET}")
                input("Pressione Enter...")
                continue
            
            cpf_formatado = formatar_cpf(cpf_raw)
            
            # Verificar se já existe
            if any(c['cpf'] == cpf_formatado for c in clientes):
                cliente_existente = next(c for c in clientes if c['cpf'] == cpf_formatado)
                print(f"{AMARELO}⚠️ Este CPF já pertence ao cliente: {cliente_existente['nome']}{RESET}")
                input("Pressione Enter...")
                continue
                
            telefone = input("Telefone / WhatsApp: ").strip()
            email = input("E-mail: ").strip()
            cidade = input("Cidade / Estado: ").strip()
            
            novo_c = {
                "id": len(clientes) + 1,
                "nome": nome,
                "cpf": cpf_formatado,
                "telefone": telefone,
                "email": email,
                "cidade": cidade,
                "data_cadastro": datetime.now().strftime("%d/%m/%Y")
            }
            clientes.append(novo_c)
            salvar_dados(ARQ_CLIENTES, clientes)
            print(f"{VERDE}✔ Cliente cadastrado com sucesso!{RESET}")
            input("Pressione Enter...")
            
        elif opcao == "2":
            if not clientes:
                print(f"{AMARELO}Nenhum cliente cadastrado.{RESET}")
                input("Pressione Enter...")
                continue
                
            print(f"\n{CIANO}--- PESQUISAR CLIENTES ---{RESET}")
            termo = input("Digite parte do nome ou CPF para pesquisar: ").lower().strip()
            encontrados = [c for c in clientes if termo in c['nome'].lower() or termo in c['cpf']]
            
            if not encontrados:
                print(f"{AMARELO}Nenhum cliente encontrado com esse termo.{RESET}")
            else:
                print(f"\n{VERDE}Encontrados ({len(encontrados)}):{RESET}")
                for i, c in enumerate(encontrados, 1):
                    print(f"{i}. {c['nome']} | CPF: {c['cpf']} | Tel: {c['telefone']}")
            input("\nPressione Enter para continuar...")
            
        elif opcao == "0":
            break

# --- MÓDULO FINANCEIRO ---
def menu_financeiro():
    financeiro = carregar_dados(ARQ_FINANCEIRO)
    while True:
        limpar_ecra()
        print(f"{CIANO}=== 💰 CONTROLO FINANCEIRO ==={RESET}")
        print("1. Registar Conta a Receber / Atendimento")
        print("2. Listar Contas e Status")
        print("3. Registar Pagamento / Baixa Parcial ou Total")
        print("0. Voltar ao Menu Principal")
        
        opcao = input(f"{ROXO}Escolha uma opção: {RESET}")
        
        if opcao == "1":
            cliente = input("Nome do Cliente: ").strip()
            descricao = input("Descrição do serviço/produto: ").strip()
            try:
                valor = float(input("Valor total (R$): ").replace(',', '.'))
            except ValueError:
                print(f"{VERMELHO}Valor inválido!{RESET}")
                input("Pressione Enter...")
                continue
                
            registro = {
                "id": len(financeiro) + 1,
                "cliente": cliente,
                "descricao": descricao,
                "valor_total": valor,
                "valor_pago": 0.0,
                "saldo_restante": valor,
                "status": "🔴 PENDENTE",
                "data": datetime.now().strftime("%d/%m/%Y")
            }
            financeiro.append(registro)
            salvar_dados(ARQ_FINANCEIRO, financeiro)
            print(f"{VERDE}✔ Registo financeiro criado com sucesso!{RESET}")
            input("Pressione Enter...")
            
        elif opcao == "2":
            if not financeiro:
                print(f"{AMARELO}Nenhum registo financeiro encontrado.{RESET}")
                input("Pressione Enter...")
                continue
            limpar_ecra()
            print(f"{CIANO}--- LISTA FINANCEIRA ---{RESET}")
            for f in financeiro:
                print(f"[{f['id']}] {f['cliente']} - {f['descricao']} | Total: R$ {f['valor_total']:.2f} | Pago: R$ {f['valor_pago']:.2f} | Restante: R$ {f['saldo_restante']:.2f} | {f['status']}")
            input("\nPressione Enter para continuar...")
            
        elif opcao == "3":
            try:
                reg_id = int(input("Digite o ID do registo para dar baixa no pagamento: "))
            except ValueError:
                print(f"{VERMELHO}ID inválido!{RESET}")
                input("Pressione Enter...")
                continue
                
            alvo = next((f for f in financeiro if f['id'] == reg_id), None)
            if not alvo:
                print(f"{VERMELHO}Registo não encontrado.{RESET}")
                input("Pressione Enter...")
                continue
                
            print(f"Devedor: {alvo['cliente']} | Restante: R$ {alvo['saldo_restante']:.2f}")
            try:
                pagamento = float(input("Valor a pagar agora (R$): ").replace(',', '.'))
            except ValueError:
                print(f"{VERMELHO}Valor inválido!{RESET}")
                input("Pressione Enter...")
                continue
                
            if pagamento > alvo['saldo_restante']:
                print(f"{VERMELHO}O pagamento não pode ser maior que o saldo restante!{RESET}")
                input("Pressione Enter...")
                continue
                
            alvo['valor_pago'] += pagamento
            alvo['saldo_restante'] = alvo['valor_total'] - alvo['valor_pago']
            
            if alvo['saldo_restante'] == 0:
                alvo['status'] = "🟢 PAGO"
            elif alvo['valor_pago'] > 0:
                alvo['status'] = "🟡 PARCIAL"
            else:
                alvo['status'] = "🔴 PENDENTE"
                
            salvar_dados(ARQ_FINANCEIRO, financeiro)
            print(f"{VERDE}✔ Pagamento registrado com sucesso! Novo saldo: R$ {alvo['saldo_restante']:.2f} ({alvo['status']}){RESET}")
            input("Pressione Enter...")
        elif opcao == "0":
            break

# --- DASHBOARD & AVISOS ---
def exibir_dashboard():
    clientes = carregar_dados(ARQ_CLIENTES)
    financeiro = carregar_dados(ARQ_FINANCEIRO)
    
    total_recebido = sum(f['valor_pago'] for f in financeiro)
    a_receber = sum(f['saldo_restante'] for f in financeiro)
    pendentes_qtd = len([f for f in financeiro if f['status'] != "🟢 PAGO"])
    
    limpar_ecra()
    print(f"{CIANO}╔══════════════════════════════════════════╗{RESET}")
    print(f"{CIANO}║{RESET}                 {NEGRITO}{BRANCO}DASHBOARD{RESET}                {CIANO}║{RESET}")
    print(f"{CIANO}╠══════════════════════════════════════════╣{RESET}")
    print(f"{CIANO}║{RESET} 👥 Clientes registados....... {str(len(clientes)).ljust(10)} {CIANO}║{RESET}")
    print(f"{CIANO}║{RESET} 💰 Total recebido........ R$ {f'{total_recebido:.2f}'.ljust(9)} {CIANO}║{RESET}")
    print(f"{CIANO}║{RESET} 🟡 A receber............. R$ {f'{a_receber:.2f}'.ljust(9)} {CIANO}║{RESET}")
    print(f"{CIANO}║{RESET} 🔴 Contas em aberto/parcial.. {str(pendentes_qtd).ljust(10)} {CIANO}║{RESET}")
    print(f"{CIANO}╚══════════════════════════════════════════╝{RESET}")
    
    print(f"\n{ROXO}🔔 AVISOS DO SISTEMA:{RESET}")
    if pendentes_qtd > 0:
        print(f"{AMARELO}⚠️ Existem {pendentes_qtd} contas com pagamento pendente ou parcial.{RESET}")
    else:
        print(f"{VERDE}✔ Nenhuma pendência financeira crítica no momento.{RESET}")
    input("\nPressione Enter para voltar ao menu...")

# --- SOBRE O SISTEMA ---
def exibir_sobre():
    limpar_ecra()
    print(f"{CIANO}╔══════════════════════════════════════════╗{RESET}")
    print(f"{CIANO}║{RESET}          {NEGRITO}{BRANCO}PRIMETECH SOLUTIONS{RESET}             {CIANO}║{RESET}")
    print(f"{CIANO}║{RESET}           {ROXO}SISTEMA DE GESTÃO{RESET}              {CIANO}║{RESET}")
    print(f"{CIANO}╠══════════════════════════════════════════╣{RESET}")
    print(f"{CIANO}║{RESET} Versão: 1.0.0                            {CIANO}║{RESET}")
    print(f"{CIANO}║{RESET} Desenvolvido por: Daniela Reis           {CIANO}║{RESET}")
    print(f"{CIANO}║{RESET} Tecnologia: Python & JSON CRUD           {CIANO}║{RESET}")
    print(f"{CIANO}║{RESET}                                          {CIANO}║{RESET}")
    print(f"{CIANO}║{RESET} Sistema desenvolvido para gerenciar      {CIANO}║{RESET}")
    print(f"{CIANO}║{RESET} clientes, dados e controlos financeiros. {CIANO}║{RESET}")
    print(f"{CIANO}╚══════════════════════════════════════════╝{RESET}")
    input("\nPressione Enter para voltar...")

# --- MENU PRINCIPAL ---
def main():
    if not sistema_login():
        return
        
    while True:
        limpar_ecra()
        print(f"{CIANO}╔══════════════════════════════════════════════════════╗{RESET}")
        print(f"{CIANO}║{RESET}              {NEGRITO}{BRANCO}PRIMETECH SOLUTIONS{RESET}                     {CIANO}║{RESET}")
        print(f"{CIANO}║{RESET}               {ROXO}SISTEMA DE GESTÃO{RESET}                      {CIANO}║{RESET}")
        print(f"{CIANO}╠══════════════════════════════════════════════════════╣{RESET}")
        print(f"{CIANO}║{RESET}                                                      {CIANO}║{RESET}")
        print(f"{CIANO}║{RESET}  1. 👥 CLIENTES                                      {CIANO}║{RESET}")
        print(f"{CIANO}║{RESET}  2. 💰 FINANCEIRO (Recebimentos e Baixas)            {CIANO}║{RESET}")
        print(f"{CIANO}║{RESET}  3. 📊 DASHBOARD & AVISOS                            {CIANO}║{RESET}")
        print(f"{CIANO}║{RESET}  8. ℹ️  SOBRE O SISTEMA                              {CIANO}║{RESET}")
        print(f"{CIANO}║{RESET}                                                      {CIANO}║{RESET}")
        print(f"{CIANO}║{RESET}  0. 🚪 SAIR                                          {CIANO}║{RESET}")
        print(f"{CIANO}║{RESET}                                                      {CIANO}║{RESET}")
        print(f"{CIANO}╚══════════════════════════════════════════════════════╝{RESET}")
        
        opcao = input(f"{ROXO}Escolha uma opção do menu: {RESET}").strip()
        
        if opcao == "1":
            menu_clientes()
        elif opcao == "2":
            menu_financeiro()
        elif opcao == "3":
            exibir_dashboard()
        elif opcao == "8":
            exibir_sobre()
        elif opcao == "0":
            print(f"\n{VERDE}A encerra o sistema PrimeTech. Até breve!{RESET}")
            break
        else:
            print(f"{VERMELHO}❌ Opção inválida! Escolha uma opção de 0 a 8.{RESET}")
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
