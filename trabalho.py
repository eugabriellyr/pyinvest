# PROJETO PYINVEST - SIMULADOR DE INVESTIMENTOS
# Disciplina: Algoritmos e Programação I — Mackenzie

# Bibliotecas utilizadas:
# math       --> funções matematicas (potencia (math.pow), arredondamento para o menor número int (math.floor))
# random     --> sorteio de valores aleatorios (simulação de risco do Fii)
# statistics --> calculos estatisticos (média, mediana, desvio padrão)
# datetime   --> data atual e data estimada de resgate
# locale     --> formatação de valores no padrão monetario do Brasil (R$)
# ============================================================

import math
import random
import statistics
import datetime
import locale

# Configura o programa para usar o padrão brasileiro:
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# ============================================================
# FUNÇÃO: converter_taxa
# OBJETIVO: Converter a taxa do CDI de anual para mensal

# Por que não dividir por 12? Juros compostos não funciona de forma linear, dividir por 12 daria uma aproximação errada
# Formula correta é: (1 + taxa_anual)^(1/12) - 1

# Exemplo:
# CDI anual = 13%  -->  CDI mensal = 1,024% ao mes

def converter_taxa(cdi_anual):
    cdi_anual  = cdi_anual / 100  # Converte de porcentagem para decimal (ex: 13% --> 0.13)
    cdi_mensal = math.pow((1 + cdi_anual), 1/12) - 1  # Formula de conversão composta
    return cdi_mensal

# ============================================================
# FUNÇÃO: calcular_cdb
# OBJETIVO: Calcular o valor final do investimento em CDB
#
# O CDB rende um percentual do CDI - ex: 110% do CDI
# Aplica juros compostos no capital inicial e no aporte mensal
# Desconta o Imposto de Renda (IR) apenas sobre o LUCRO, usando a tabela regressiva (quanto mais tempo, menos imposto)

def calcular_cdb(capital_inicial, cdi_mensal, percentual_cdb, meses, aporte_mensal, total_investido):
    # Taxa real do CDB = CDI mensal × percentual contratado
    # Como o CDI mensal esta em decimal, transforma o percentual do CDB em decimal também
    taxa_cdb_mensal = cdi_mensal * (percentual_cdb / 100)

    # JUROS COMPOSTOS DO CAPITAL INICIAL
    # Formula: M = C × (1 + i)^n
    # M = montante final, C = capital inicial, i = taxa mensal, n = número de meses
    # O capital inicial cresce mes a mes sobre ele mesmo (juros sobre juros)
    montante_capital_final = capital_inicial * math.pow(1 + taxa_cdb_mensal, meses)

    # JUROS COMPOSTOS DO APORTE MENSAL
    # Formula: M = PMT × ((1 + i)^n - 1) / i
    # PMT = aporte mensal --> cada aporte também rende juros compostos
    # Essa formula ja considera que cada aporte entra em um mes diferente
    montante_aporte_final = aporte_mensal * (math.pow(1 + taxa_cdb_mensal, meses) - 1) / taxa_cdb_mensal

    # Montante total = capital inicial rendendo + aportes mensais rendendo
    montante_final_total = montante_capital_final + montante_aporte_final

    # Lucro = quanto o dinheiro rendeu (montante total - o que foi investido)
    lucro = montante_final_total - total_investido

    # Converter meses em dias para aplicar a tabela regressiva de IR (Imposto de Renda)
    dias = meses * 30

    # TABELA REGRESSIVA DE IR:
    # Imposto so sobre o lucro
    # Quanto mais tempo investido, menor a aliquota - porcentagem de imposto
    if dias <= 180:
        aliquota = 0.225   
        #22,5% de imposto (sacou rapido, paga mais)

    elif dias <= 360:
        aliquota = 0.20    
        #20% de imposto

    elif dias <= 720:
        aliquota = 0.175   
        #17,5% de imposto
        
    else:
        aliquota = 0.15    
        #15% de imposto

    # Imposto descontado = lucro × aliquota
    imposto_descontado = lucro * aliquota

    # Valor final = montante total - imposto (o que o investidor recebe no bolso)
    valor_final_recebido = montante_final_total - imposto_descontado

    return valor_final_recebido


# ============================================================
# FUNÇÃO: calcular_lci_lca
# OBJETIVO: Calcular o valor final do investimento em LCI/LCA
#
# Funciona igual ao CDB (CDI × percentual + juros compostos), mas com uma grande vantagem: é ISENTO de Imposto de Renda
# Por isso, mesmo rendendo menos % do CDI, pode superar o CDB

def calcular_lci_lca(capital_inicial, aporte_mensal, meses, cdi_mensal, percentual_lci_lca):
    # Taxa real da LCI/LCA = CDI mensal × percentual contratado
    # Como o CDI mensal esta em decimal, transforma o percentual LCI/LCA em decimal também
    taxa_lci_lca_mensal = cdi_mensal * (percentual_lci_lca / 100)

    # Juros compostos do capital inicial
    montante_capital_final = capital_inicial * math.pow(1 + taxa_lci_lca_mensal, meses)

    # Juros compostos do aporte mensal
    montante_aporte_final = aporte_mensal * (math.pow(1 + taxa_lci_lca_mensal, meses) - 1) / taxa_lci_lca_mensal

    # Montante total
    montante_final_total = montante_capital_final + montante_aporte_final

    # Sem desconto de IR --> valor final é o montante total direto
    valor_final_recebido = montante_final_total

    return valor_final_recebido


# ============================================================
# FUNÇÃO: calcular_poupanca
# OBJETIVO: Calcular o valor final do investimento na Poupança
#
# A poupança tem taxa FIXA de 0,5% ao mes, independente do CDI
# Também é isenta de IR, porém custuma render menos que CDB e LCI

def calcular_poupanca(capital_inicial, aporte_mensal, meses):
    # Taxa fixa da poupança: sempre 0,5% ao mes --> 0.005 em decimal
    taxa_poupanca = 0.005

    # Juros compostos do capital inicial
    montante_capital_final = capital_inicial * math.pow(1 + taxa_poupanca, meses)

    # Juros compostos do aporte mensal
    montante_aporte_final = aporte_mensal * (math.pow(1 + taxa_poupanca, meses) - 1) / taxa_poupanca

    # Montante total (sem IR)
    montante_final_total = montante_capital_final + montante_aporte_final

    valor_final_recebido = montante_final_total

    return valor_final_recebido


# ============================================================
# FUNÇÃO: calcular_fii
# OBJETIVO: Calcular o valor final do FII com simulação de risco
#
# FII - Fundo de Investimento Imobiliario tem risco de mercado, ou seja, o valor pode variar pra cima ou pra baixo
# Simulando esse risco:
    # 1. Calcular o montante base com juros compostos
    # 2. Gerar 5 simulações, cada uma com variação aleatoria entre -3% e +3%
    # 3. Calcular média, mediana e desvio padrão das 5 simulações
    # 4. Usar a MÉDIA como valor oficial do FII no relatorio

def calcular_fii(capital_inicial, aporte_mensal, meses, rentabilidade_fii):
    # Converte a rentabilidade de porcentagem para decimal ex: 0.8% --> 0.008
    taxa_fii = rentabilidade_fii / 100

    # Juros compostos do capital inicial
    montante_capital_final = capital_inicial * math.pow(1 + taxa_fii, meses)

    # Juros compostos do aporte mensal
    montante_aporte_final = aporte_mensal * (math.pow(1 + taxa_fii, meses) - 1) / taxa_fii

    # Montante base (sem variação de risco ainda)
    montante_final_total = montante_capital_final + montante_aporte_final

    # SIMULAÇÃO DE RISCO DE MERCADO:
    # random.uniform(-0.03, 0.03) sorteia um número aleatorio entre -3% e +3%
    # Cada simulação é independente --> sorteia uma variação diferente
    # Multiplica o montante base por (1 + variação) para aplicar o risco, calculando juros compostos
    variacao1 = montante_final_total * (1 + random.uniform(-0.03, 0.03))
    variacao2 = montante_final_total * (1 + random.uniform(-0.03, 0.03))
    variacao3 = montante_final_total * (1 + random.uniform(-0.03, 0.03))
    variacao4 = montante_final_total * (1 + random.uniform(-0.03, 0.03))
    variacao5 = montante_final_total * (1 + random.uniform(-0.03, 0.03))

    # ESTATiSTICAS das 5 simulações:
    # Média   --> valor central, usado como resultado padrão do FII
    # Mediana --> valor do meio quando os 5 são ordenados
    # Desvio  --> o quanto os valores variaram entre si (mede o risco)
    media         = statistics.mean([variacao1, variacao2, variacao3, variacao4, variacao5])
    mediana       = statistics.median([variacao1, variacao2, variacao3, variacao4, variacao5])
    desvio_padrao = statistics.stdev([variacao1, variacao2, variacao3, variacao4, variacao5])

    return media, mediana, desvio_padrao


# ============================================================
# FUNÇÃO: calcular_total_investido
# OBJETIVO: Calcular o total de dinheiro colocado pelo investidor
#
# Total = capital inicial + (aporte mensal × número de meses)
# Esse valor NÃO inclui juros, é so o que foi depositado.

def calcular_total_investido(capital_inicial, aporte_mensal, prazo_investimento):
    total_investido = capital_inicial + (aporte_mensal * prazo_investimento)
    return total_investido


# ============================================================
# FUNÇÃO: gerar_relatorio
# OBJETIVO: Exibir o relatorio final formatado com todos os resultados
#
# Contém:
        # -- Datas (simulação e resgate)
        # -- Valores finais de cada investimento
        # -- Grafico de barras ASCII proporcional
        # -- Estatisticas do FII
        # -- Se a meta foi atingida
        # -- Qual foi o melhor investimento

def gerar_relatorio(meses, total_investido, valor_investido_cdb, valor_investido_lci_lca, valor_investido_poupanca, media_fii, mediana_fii, desvio_fii, meta):

    # DATA ATUAL e DATA DE RESGATE
    data_atual = datetime.date.today()  # Pega a data de hoje 
    # Soma os dias totais do investimento (30 dias por mes, conforme o PDF
    data_resgate = data_atual + datetime.timedelta(days=meses * 30)

    # GRÁFICO DE BARRAS
    # Regra: o maior valor recebe 50 blocos = barra cheia
    # Os outros são proporcionais a ele (regra de tres)

    # Exemplo:
    # Maior valor = R$ 28.000 --> 50 blocos
    # CDB         = R$ 25.000 --> ?? blocos
    # CDB         = R$ 25.000 --> (25000/28000) × 50 = 44 blocos
 

    # Identifica o maior valor entre todos os investimentos
    maior_valor = max(valor_investido_cdb, valor_investido_lci_lca, valor_investido_poupanca, media_fii)

    # Calcula quantos blocos cada investimento terá (proporção × 50)
    # math.floor arredonda SEMPRE para baixo --> garante no maximo 50 blocos
    blocos_cdb      = math.floor((valor_investido_cdb      / maior_valor) * 50)
    blocos_lci_lca  = math.floor((valor_investido_lci_lca  / maior_valor) * 50)
    blocos_poupanca = math.floor((valor_investido_poupanca / maior_valor) * 50)
    blocos_fii      = math.floor((media_fii                / maior_valor) * 50)

    # Constroi as barras usando multiplicação de string
    barra_cdb      = "█" * blocos_cdb
    barra_lci_lca  = "█" * blocos_lci_lca
    barra_poupanca = "█" * blocos_poupanca
    barra_fii      = "█" * blocos_fii

    # META FINANCEIRA 
    # Verifica se o maior valor entre todos os investimentos atingiu a meta desejada pelo investidor
    # Se nem o maior atingiu --> nenhum atingiu

    if maior_valor >= meta:
        resultado_meta = "Meta atingida? Sim! :)"
    else:
        resultado_meta = "Meta atingida? Não :("

    # MELHOR INVESTIMENTO
    # Compara os 4 valores e identifica qual teve maior retorno liquido
    # Para o FII, usa a média das 5 simulações como valor oficial

    if valor_investido_cdb >= valor_investido_lci_lca and valor_investido_cdb >= valor_investido_poupanca and valor_investido_cdb >= media_fii:
        melhor = f"CDB com {locale.currency(valor_investido_cdb, grouping=True)}"

    elif valor_investido_lci_lca >= valor_investido_cdb and valor_investido_lci_lca >= valor_investido_poupanca and valor_investido_lci_lca >= media_fii:
        melhor = f"LCI/LCA com {locale.currency(valor_investido_lci_lca, grouping=True)}"

    elif valor_investido_poupanca >= valor_investido_cdb and valor_investido_poupanca >= valor_investido_lci_lca and valor_investido_poupanca >= media_fii:
        melhor = f"Poupança com {locale.currency(valor_investido_poupanca, grouping=True)}"

    else:
        melhor = f"FII (Média) com {locale.currency(media_fii, grouping=True)}"

    # IMPRESSÃO DO RELAToRIO
    # locale.currency(valor, grouping=True) formata no padrão brasileiro
     # Ex: locale.currency(12345.67, grouping=True) --> R$ 12.345,67
    # O 'grouping=True' formata os valores em milhares, separando com "."


    print("=" * 60)
    print(f"RELÁTORIO PYINVEST - {data_atual.strftime('%d/%m/%Y')}")
    print(f"Data estimada de resgate: {data_resgate.strftime('%d/%m/%Y')}")
    print(f"Total investido: {locale.currency(total_investido, grouping=True)}")
    print("-" * 60)

    # Resultados e graficos de cada modalidade de investimento
    print(f"CDB          : {locale.currency(valor_investido_cdb, grouping=True)}")
    print(f"Gráfico      : {barra_cdb}")
    print(f"LCI/LCA      : {locale.currency(valor_investido_lci_lca, grouping=True)}")
    print(f"Gráfico      : {barra_lci_lca}")
    print(f"Poupança     : {locale.currency(valor_investido_poupanca, grouping=True)}")
    print(f"Gráfico      : {barra_poupanca}")
    print(f"FII (Média)  : {locale.currency(media_fii, grouping=True)}")
    print(f"Gráfico      : {barra_fii}")
    print("-" * 60)

    # Estatisticas do FII
    print(f"Estatisticas FII (Mediana): {locale.currency(mediana_fii, grouping=True)}")
    print(f"Desvio Padrão FII: {locale.currency(desvio_fii, grouping=True)}")

    # Meta e melhor opção
    print(resultado_meta)
    print(f"\nMelhor opção: {melhor}")
    print("=" * 60)


# ============================================================
# FUNÇÃO: validar_dados
# OBJETIVO: Verificar se os dados inseridos pelo usuario são validos
#
# Capital, aporte e prazo precisam ser positivos (maiores que zero)
# Se algum for invalido, exibe mensagem de erro e encerra o programa

def validar_dados(capital_inicial, aporte_mensal, prazo_investimento):
    # DÚVIDA AQUI, PESQUISANDO ENTENDI QUE O APORTE MENSAL PODE SER ZERO?? 
    # Porém eu teria que mexer nas outras funções para lidar com isso
    # if capital_inicial <= 0 or aporte_mensal < 0 or prazo_investimento <= 0:
    if capital_inicial <= 0 or aporte_mensal <= 0 or prazo_investimento <= 0:
        print("Erro! Capital, aporte e prazo devem ser valores positivos.")
        exit()  # Encerra o programa imediatamente


# ============================================================
# FUNÇÃO: programa_principal
# OBJETIVO: Função principal que organiza e executa tudo
#
# Fluxo:
    # 1. Pede os dados ao usuario
    # 2. Valida os dados
    # 3. Chama as funções de calculo
    # 4. Gera o relatorio final
def programa_principal():
    print("=" * 20, "PYINVEST", "=" * 20)

    # ENTRADA DE DADOS 
    capital_inicial    = float(input("Capital Inicial que ira investir (R$): "))
    aporte_mensal      = float(input("Aporte Mensal (R$): "))
    prazo_investimento = int(input("Prazo do investimento (meses): "))

    # Valida antes de continuar PARA se dados for invalidos
    validar_dados(capital_inicial, aporte_mensal, prazo_investimento)

    #  ENTRADA DE DADOS RESTANTES
    cdi_anual          = float(input("Digite CDI Anual (%): "))
    percentual_cdb     = float(input("Digite o Percentual do CDI aplicado ao CDB (%): "))
    percentual_lci_lca = float(input("Digite o Percentual do CDI aplicado à LCI/LCA (%): "))
    rentabilidade_fii  = float(input("Digite a Rentabilidade mensal esperada do FII (%): "))
    meta_financeira    = float(input("Digite a Meta financeira desejada (R$): "))

    # CaLCULOS
    # Converte o CDI anual para mensal (usado no CDB e LCI/LCA)
    cdi_mensal = converter_taxa(cdi_anual)

    # Calcula o total investido (capital + aportes, sem juros)
    total_investido = calcular_total_investido(capital_inicial, aporte_mensal, prazo_investimento)

    # Calcula o valor final de cada investimento
    valor_investido_cdb     = calcular_cdb(capital_inicial, cdi_mensal, percentual_cdb, prazo_investimento, aporte_mensal, total_investido)
    valor_investido_lci_lca = calcular_lci_lca(capital_inicial, aporte_mensal, prazo_investimento, cdi_mensal, percentual_lci_lca)
    valor_investido_poupanca = calcular_poupanca(capital_inicial, aporte_mensal, prazo_investimento)

    # FII retorna 3 valores: média, mediana e desvio padrão
    media_fii, mediana_fii, desvio_fii = calcular_fii(capital_inicial, aporte_mensal, prazo_investimento, rentabilidade_fii)

    # RELAToRIO 
    # Passa todos os valores calculados para gerar o relatorio final
    gerar_relatorio(prazo_investimento, total_investido, valor_investido_cdb, valor_investido_lci_lca, valor_investido_poupanca, media_fii, mediana_fii, desvio_fii, meta_financeira)

# Chamada da função principal para iniciar o programa
programa_principal()