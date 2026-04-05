# PROJETO PYINVEST - SIMULADOR DE INVESTIMENTOS
import math
import random 
import datetime
import statistics 
import locale

# Configura o padrão  para dinheiro (R$)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Função para validar se as entradas são positivas 
def check_dados(capital, aporte, prazo):
    if capital <= 0 or aporte <= 0 or prazo <= 0:
        print("Erro: Os valores de capital, aporte e prazo devem ser maiores que zero.")
        exit() # PARA O PROGRAMA

# Converte taxa anual para mensal, usando juros compostos
def convercao_cdi(taxa_anual):
    taxa_decimal = taxa_anual / 100
    # Formula (1 + i_anual)^(1/12) - 1
    taxa_mensal = (1 + taxa_decimal) ** (1/12) - 1
    return taxa_mensal

# Calcula o total que saiu do bolso 
def calculo_total_investido(capital, aporte, prazo):
    return capital + (aporte * prazo)

# Calculo do CDB com Tabela Regressiva de IR 
def calculo_cdb(capital, aporte, prazo, taxa_cdi_mensal, percentual_cdi):
    # Ajusta a taxa de acordo com o percentual do CDI 
    taxa_final = taxa_cdi_mensal * (percentual_cdi / 100)
    
    # Formulas de Juros Compostos para capital e aportes mensais 
    valor_final_capital = capital * (1 + taxa_final) ** prazo
    valor_final_aportes = aporte * (((1 + taxa_final) ** prazo - 1) / taxa_final)
    valor_bruto = valor_final_capital + valor_final_aportes
    
    # Calculo do imposto de renda - sobre o lucro
    lucro = valor_bruto - (capital + (aporte * prazo))
    
    # Tabela Regressiva baseada em dias - PDF
    dias = prazo * 30
    if dias <= 180:
        aliquota = 0.225
        #22.5% 
    elif dias <= 360:
        aliquota = 0.20
        #20% 
    elif dias <= 720:
        aliquota = 0.175
        #17.5% 
    else:
        aliquota = 0.15
        #15% 
    
    imposto = lucro * aliquota
    return valor_bruto - imposto

# Calculo LCI/LCA - sem imposto 
def calculo_lci_lca(capital, aporte, prazo, taxa_cdi_mensal, percentual_cdi):
    taxa_final = taxa_cdi_mensal * (percentual_cdi / 100)
    v_cap = capital * (1 + taxa_final) ** prazo
    v_apo = aporte * (((1 + taxa_final) ** prazo - 1) / taxa_final)
    return v_cap + v_apo

# Calculo da Poupança - 5% ao mês
def calculo_poupanca(capital, aporte, prazo):
    taxa_fixa = 0.005 
    
    v_cap = capital * (1 + taxa_fixa) ** prazo
    v_apo = aporte * (((1 + taxa_fixa) ** prazo - 1) / taxa_fixa)
    return v_cap + v_apo

# Simulacaoo de FII com risco 
def calculo_fii(capital, aporte, prazo, rentabilidade_espe):
    taxa = rentabilidade_espe / 100
    valor_base = (capital * (1 + taxa) ** prazo) + (aporte * (((1 + taxa) ** prazo - 1) / taxa))
    
    # 5 simulacoes com variacao aleatoria - -3% e +3% 
    s1 = valor_base * (1 + random.uniform(-0.03, 0.03))
    s2 = valor_base * (1 + random.uniform(-0.03, 0.03))
    s3 = valor_base * (1 + random.uniform(-0.03, 0.03))
    s4 = valor_base * (1 + random.uniform(-0.03, 0.03))
    s5 = valor_base * (1 + random.uniform(-0.03, 0.03))
    
    # Biblioteca statistics - PDF
    # Passei os valores diretamente para nao usar lista 
    media = statistics.mean([s1, s2, s3, s4, s5])
    mediana = statistics.median([s1, s2, s3, s4, s5])
    desvio = statistics.stdev([s1, s2, s3, s4, s5])
    
    return media, mediana, desvio

# Função para rodar o simulador
def simulacao_pyinvest():
    print("*"*20, "PYINVEST - ENTRADA DE DADOS", "*"*20)
    
    # Entradas minimas
    cap_ini = float(input("Capital Inicial que irá investir (R$): "))
    apo_men = float(input("Aporte Mensal (R$): "))
    meses = int(input("Prazo (meses): "))
    
    # Chamada validacao 
    check_dados(cap_ini, apo_men, meses)
    
    # Outros Dados
    cdi_anual = float(input("Digite CDI Anual (%): "))
    per_cdb = float(input("Digite o Percentual do CDI no CDB (%): "))
    per_lci = float(input("Digite o Percentual do CDI na LCI/LCA (%): "))
    rent_fii = float(input("Digite a Rentabilidade mensal esperada do FII (%): "))
    meta = float(input("Digite a Meta financeira desejada (R$): "))
    
    # Chamando os calculos
    taxa_cdi_m = convercao_cdi(cdi_anual)
    total_inv = calculo_total_investido(cap_ini, apo_men, meses)
    
    res_cdb = calculo_cdb(cap_ini, apo_men, meses, taxa_cdi_m, per_cdb)
    res_lci = calculo_lci_lca(cap_ini, apo_men, meses, taxa_cdi_m, per_lci)
    res_poup = calculo_poupanca(cap_ini, apo_men, meses)
    media_fii, mediana_fii, desvio_fii = calculo_fii(cap_ini, apo_men, meses, rent_fii)
    
    # Chamada Datas
    data_hoje = datetime.date.today()
    data_resgate = data_hoje + datetime.timedelta(days=meses * 30)
    
    # Logica para o Graficos e Melhor escolha
    maior_valor = res_cdb
    if res_lci > maior_valor: maior_valor = res_lci
    if res_poup > maior_valor: maior_valor = res_poup
    if media_fii > maior_valor: maior_valor = media_fii
    
    # Calculo das barras - base 50 blocos
    # Multiplicação de string 
    barra_cdb = "█" * int((res_cdb * 50) / maior_valor)
    barra_lci = "█" * int((res_lci * 50) / maior_valor)
    barra_poup = "█" * int((res_poup * 50) / maior_valor)
    barra_fii = "█" * int((media_fii * 50) / maior_valor)
    
    # Por fim, exibe tudo
    print("\n" + "="*60)
    print(f"RELATÓRIO PYINVEST - {data_hoje.strftime('%d/%m/%Y')}") 
    print(f"Data estimada de resgate: {data_resgate.strftime('%d/%m/%Y')}") 
    print(f"Total investido: {locale.currency(total_inv, grouping=True)}")
    print("-" * 60)
    
    print(f"CDB:      {locale.currency(res_cdb, grouping=True)}")
    print(f"Gráfico:  {barra_cdb}")
    print(f"LCI/LCA:  {locale.currency(res_lci, grouping=True)}")
    print(f"Gráfico:  {barra_lci}")
    print(f"Poupança: {locale.currency(res_poup, grouping=True)}")
    print(f"Gráfico:  {barra_poup}")
    print(f"FII (Méd): {locale.currency(media_fii, grouping=True)}")
    print(f"Gráfico:  {barra_fii}")
    
    print("-" * 60)
    print(f"Estatísticas FII (Mediana): {locale.currency(mediana_fii, grouping=True)}") 
    print(f"Desvio Padrão FII: {locale.currency(desvio_fii, grouping=True)}")
    
    # Meta Financeira 
    if maior_valor >= meta:
        print(f"Meta atingida? Sim")
    else:
        print(f"Meta atingida? Não")
        
    # Melhor Opcao
    vencedor = "CDB"
    if res_lci == maior_valor: vencedor = "LCI/LCA"
    elif res_poup == maior_valor: vencedor = "Poupança"
    elif media_fii == maior_valor: vencedor = "FII (Média)"
    
    print(f"Melhor opção: {vencedor} com {locale.currency(maior_valor, grouping=True)}")
    print("="*60)

# Execução do programa
simulacao_pyinvest()