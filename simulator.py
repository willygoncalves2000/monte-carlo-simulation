# ==========================================================
# MÓDULO: simulador.py
# Simulação completa do projeto de construção via Monte Carlo
# ==========================================================
# Depende de: fases.py e distribuições.py
# ==========================================================

import matplotlib.pyplot as plt
import os

from fases import (
    simular_preparacao, simular_fundacao, simular_laje,
    simular_alvenaria, simular_acabamento, simular_pintura
)
from distribuicoes import converter_lognormal
import statistics


# ==========================================================
# 1. Simular uma obra completa
# ==========================================================
def simular_projeto(param):
    """Executa uma simulação completa de todas as fases do projeto."""

    # ----------------------------
    # Preparação do terreno
    # ----------------------------
    T1, C1 = simular_preparacao(
        param['prep']['o'], param['prep']['m'], param['prep']['p'],
        param['prep']['muM'], param['prep']['sigmaM'],
        param['prep']['muL'], param['prep']['sigmaL']
    )

    # ----------------------------
    # Fundação
    # ----------------------------
    T2, C2 = simular_fundacao(
        *param['fundacaoA']['duracao'],
        *param['fundacaoA']['custos'],
        *param['fundacaoB']['duracao'],
        *param['fundacaoB']['custos'],
        param['fundacao']['pA'],
        param['fundacao']['pG'],
        param['fundacao']['Tgeo'],
        param['fundacao']['Cgeo']
    )

    # ----------------------------
    # Laje
    # ----------------------------
    T3, C3 = simular_laje(
        param['laje']['o'], param['laje']['m'], param['laje']['p'],
        param['laje']['muM'], param['laje']['sigmaM'],
        param['laje']['muL'], param['laje']['sigmaL']
    )

    # ----------------------------
    # Alvenaria
    # ----------------------------
    T4, C4 = simular_alvenaria(
        param['alvenaria']['o'], param['alvenaria']['m'], param['alvenaria']['p'],
        param['alvenaria']['muM'], param['alvenaria']['sigmaM'],
        param['alvenaria']['muL'], param['alvenaria']['sigmaL'],
        param['alvenaria']['pR'], param['alvenaria']['Cretrabalho'],
        param['alvenaria']['Tretrabalho']
    )

    # ----------------------------
    # Acabamento
    # ----------------------------
    T5, C5 = simular_acabamento(
        param['acab']['o'], param['acab']['m'], param['acab']['p'],
        param['acab']['muM'], param['acab']['sigmaM'],
        param['acab']['muL'], param['acab']['sigmaL']
    )

    # ----------------------------
    # Pintura
    # ----------------------------
    T6, C6 = simular_pintura(
        param['pintura']['pEP'], param['pintura']['pW'],
        # Empresa A
        *param['pinturaA']['custos'],
        *param['pinturaA']['dur_bom'],
        *param['pinturaA']['dur_chuva'],
        # Empresa B
        *param['pinturaB']['custos'],
        *param['pinturaB']['dur_bom'],
        *param['pinturaB']['dur_chuva'],
    )

    # ----------------------------
    # Soma total
    # ----------------------------
    tempo_total = T1 + T2 + T3 + T4 + T5 + T6
    custo_total = C1 + C2 + C3 + C4 + C5 + C6

    return tempo_total, custo_total


# ==========================================================
# 2. Rodar múltiplas simulações
# ==========================================================
def rodar_simulacoes(param, contrato, N=10000, plot=False, nome_cenario="Cenário"):
    """
    Executa N simulações e calcula as métricas:
    - Probabilidade de prejuízo
    - Valor médio de multa (entre as simulações com atraso)
    - Custo médio total (incluindo multas)
    """
    multas = []
    custos_totais = []
    tempos_totais = []
    prejuizos = 0

    for _ in range(N):
        tempo, custo = simular_projeto(param)

        # Calcula multa
        atraso = max(0, tempo - contrato['prazo'])
        multa = atraso * contrato['multa_dia']
        custo_total_com_multa = custo + multa
        
        tempos_totais.append(tempo)
        custos_totais.append(custo_total_com_multa)
        
        if custo_total_com_multa > contrato['valor_contrato']:
            prejuizos += 1
        if atraso > 0:
            multas.append(multa)

    prob_prejuizo = prejuizos / N * 100
    multa_media = statistics.mean(multas) if multas else 0
    custo_medio = statistics.mean(custos_totais)

    resultados = {
        "Probabilidade de Prejuízo (%)": prob_prejuizo,
        "Valor Médio da Multa (R$)": multa_media,
        "Custo Médio Total (R$)": custo_medio
    }

    # ==========================================================
    # Geração e salvamento dos histogramas
    # ==========================================================
    if plot:
        pasta = os.path.join("assets", "histogramas_cenarios")
        os.makedirs(pasta, exist_ok=True)

        # Histograma de custos
        plt.figure(figsize=(8, 4))
        plt.hist(custos_totais, bins=60, color='#5DADE2', edgecolor='black')
        plt.title(f"Distribuição dos Custos Totais - {nome_cenario}")
        plt.xlabel("Custo Total (R$)")
        plt.ylabel("Frequência")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        caminho_custo = os.path.join(pasta, f"{nome_cenario.lower()}_custo.png")
        plt.savefig(caminho_custo, dpi=300)
        plt.close()

        # Histograma de tempos
        plt.figure(figsize=(8, 4))
        plt.hist(tempos_totais, bins=60, color='#58D68D', edgecolor='black')
        plt.title(f"Distribuição dos Tempos Totais - {nome_cenario}")
        plt.xlabel("Tempo Total (dias)")
        plt.ylabel("Frequência")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        caminho_tempo = os.path.join(pasta, f"{nome_cenario.lower()}_tempo.png")
        plt.savefig(caminho_tempo, dpi=300)
        plt.close()

        print(f"\nGráficos salvos em: {os.path.abspath(pasta)}")
        print(f"- {os.path.basename(caminho_custo)}")
        print(f"- {os.path.basename(caminho_tempo)}")

    return resultados


# ==========================================================
# 3. Execução para o Cenário 1 (Edifício)
# ==========================================================
def executar_cenario_1():
    """Configura os parâmetros do Cenário 1 e executa a simulação."""
    param = {
        "prep": {"o":10, "m":14, "p":20, "muM":120000, "sigmaM":30000, "muL":150000, "sigmaL":35000},
        "fundacaoA": {
            "duracao": (30, 40, 55),
            "custos": (2700000, 300000, 2300000, 250000)
        },
        "fundacaoB": {
            "duracao": (25, 34, 48),
            "custos": (3000000, 350000, 2100000, 260000)
        },
        "fundacao": {"pA":0.6, "pG":0.18, "Tgeo":25, "Cgeo":700000},
        "laje": {"o":80, "m":100, "p":130, "muM":2400000, "sigmaM":300000, "muL":1800000, "sigmaL":200000},
        "alvenaria": {"o":60, "m":75, "p":95, "muM":900000, "sigmaM":120000, "muL":1600000, "sigmaL":200000,
                      "pR":0.12, "Cretrabalho":300000, "Tretrabalho":12},
        "acab": {"o":80, "m":110, "p":150, "muM":2500000, "sigmaM":350000, "muL":2500000, "sigmaL":400000},
        "pintura": {"pEP":0.6, "pW":0.2},
        "pinturaA": {
            "custos": (300000, 50000, 280000, 40000),
            "dur_bom": (12, 16, 22),
            "dur_chuva": (16, 20, 28)
        },
        "pinturaB": {
            "custos": (320000, 60000, 260000, 45000),
            "dur_bom": (10, 14, 18),
            "dur_chuva": (14, 18, 24)
        }
    }

    contrato = {
        "valor_contrato": 19000000,
        "prazo": 360,
        "multa_dia": 3000
    }

    resultados = rodar_simulacoes(param, contrato, N=1000000, plot=True, nome_cenario="Cenário 1 - Edifício")
    print("\n===== RESULTADOS — CENÁRIO 1 =====")
    for k, v in resultados.items():
        print(f"{k}: {v:,.2f}")

    print("\n--- Tomada de Decisão (Cenário 1) ---")
    criterio_prejuizo = 30  
    criterio_multa = 200000
    
    prob_prejuizo_calc = resultados["Probabilidade de Prejuízo (%)"]
    multa_media_calc = resultados["Valor Médio da Multa (R$)"]

    print(f"Critério Prejuízo: < {criterio_prejuizo:.2f}% (Resultado: {prob_prejuizo_calc:.2f}%)")
    print(f"Critério Multa Média: < R$ {criterio_multa:,.2f} (Resultado: R$ {multa_media_calc:,.2f})")

    if prob_prejuizo_calc < criterio_prejuizo and multa_media_calc < criterio_multa:
        print("\nRECOMENDAÇÃO: Aceitar Contrato")
    else:
        print("\nRECOMENDAÇÃO: Rejeitar Contrato")

# ==========================================================
# 4. Execução para o Cenário 2 (Galpão)
# ==========================================================
def executar_cenario_2():
    """Configura os parâmetros do Cenário 2 e executa a simulação."""
    param = { 
        "prep":{"o":5, "m":7, "p":12, "muM":50000, "sigmaM":12000, "muL":80000, "sigmaL":18000},
        "fundacaoA":{
            "duracao":(18, 22, 30),
            "custos":(1200000, 180000, 700000, 120000)
        },
        "fundacaoB":{
            "duracao":(15, 19, 25),
            "custos":(1300000, 200000, 650000, 110000)
        },
        "fundacao": {"pA":0.7, "pG":0.08, "Tgeo":10, "Cgeo":200000},
        "laje": {"o":18, "m":24, "p":32, "muM":1000000, "sigmaM":150000, "muL":600000, "sigmaL":100000},
        "alvenaria": {"o":8, "m":10, "p":14, "muM":125000, "sigmaM":25000, "muL":160000, "sigmaL":30000,
                      "pR":0.05, "Cretrabalho":60000, "Tretrabalho":4},
        "acab": {"o":14, "m":18, "p":26, "muM":200000, "sigmaM":35000, "muL":300000, "sigmaL":50000},
        "pintura": {"pEP":0.5, "pW":0.3},
        "pinturaA": {
            "custos": (40000, 7000, 50000, 8000),
            "dur_bom": (6, 7, 9),
            "dur_chuva": (8, 9, 12)
        },
        "pinturaB": {
            "custos": (45000, 8000, 45000, 7000),
            "dur_bom": (5, 7, 8),
            "dur_chuva": (7, 8, 11)
        }

    }
    contrato = {
        "valor_contrato": 43000000,
        "prazo": 150,
        "multa_dia": 5000
    }

    resultados = rodar_simulacoes(param, contrato, N=1000000, plot=True, nome_cenario="Cenário 2 - Galpão")
    print("\n===== RESULTADOS — CENÁRIO 2 =====")
    for k, v in resultados.items():
        print(f"{k}: {v:,.2f}")

    print("\n--- Tomada de Decisão (Cenário 2) ---")
    criterio_prejuizo = 25
    
    prob_prejuizo_calc = resultados["Probabilidade de Prejuízo (%)"]

    print(f"Critério Prejuízo: < {criterio_prejuizo:.2f}% (Resultado: {prob_prejuizo_calc:.2f}%)")

    if prob_prejuizo_calc < criterio_prejuizo:
        print("\nRECOMENDAÇÃO: Aceitar Contrato")
    else:
        print("\nRECOMENDAÇÃO: Rejeitar Contrato")

# ==========================================================
# 5. Execução para o Cenário 3 (Centro de Saúde)
# ==========================================================
def executar_cenario_3():
    """Configura os parâmetros do Cenário 3 e executa a simulação."""
    
    param = {
        "prep": {"o":8, "m":12, "p":18, "muM":90000, "sigmaM":20000, "muL":120000, "sigmaL":25000},
        "fundacaoA": {
            "duracao": (28, 36, 48),
            "custos": (1800000, 220000, 1400000, 180000)
        },
        "fundacaoB": {
            "duracao": (25, 32, 44),
            "custos": (1900000, 260000, 1350000, 170000)
        },
        "fundacao": {"pA":0.5, "pG":0.25, "Tgeo":30, "Cgeo":800000},
        "laje": {"o":30, "m":40, "p":55, "muM":1200000, "sigmaM":170000, "muL":900000, "sigmaL":120000},
        "alvenaria": {"o":50, "m":65, "p":85, "muM":600000, "sigmaM":90000, "muL":1300000, "sigmaL":160000,
                      "pR":0.15, "Cretrabalho":400000, "Tretrabalho":15},
        "acab": {"o":70, "m":95, "p":130, "muM":2000000, "sigmaM":300000, "muL":2200000, "sigmaL":300000},
        "pintura": {"pEP":0.4, "pW":0.25},
        "pinturaA": {
            "custos": (120000, 20000, 100000, 18000),
            "dur_bom": (10, 13, 16),
            "dur_chuva": (14, 18, 22)
        },
        "pinturaB": {
            "custos": (130000, 22000, 95000, 16000),
            "dur_bom": (9, 12, 15),
            "dur_chuva": (12, 16, 20)
        }
    }

    contrato = {
        "valor_contrato": 12500000,
        "prazo": 300,
        "multa_dia": 4000
    }

    resultados = rodar_simulacoes(param, contrato, N=1000000, plot=True, nome_cenario="Cenário 3 - Centro de Saúde")
    print("\n===== RESULTADOS — CENÁRIO 3 =====")
    for k, v in resultados.items():
        print(f"{k}: {v:,.2f}")
    
    print("\n--- Tomada de Decisão (Cenário 3) ---")
    criterio_prejuizo = 15 
    criterio_multa = 50000
    
    prob_prejuizo_calc = resultados["Probabilidade de Prejuízo (%)"]
    multa_media_calc = resultados["Valor Médio da Multa (R$)"]

    print(f"Critério Prejuízo: < {criterio_prejuizo:.2f}% (Resultado: {prob_prejuizo_calc:.2f}%)")
    print(f"Critério Multa Média: < R$ {criterio_multa:,.2f} (Resultado: R$ {multa_media_calc:,.2f})")

    if prob_prejuizo_calc < criterio_prejuizo and multa_media_calc < criterio_multa:
        print("\nRECOMENDAÇÃO: Aceitar Contrato")
    else:
        print("\nRECOMENDAÇÃO: Rejeitar Contrato")

# ==========================================================
# Execução direta (todos os cenários)
# ==========================================================
if __name__ == "__main__":
    executar_cenario_1()
    executar_cenario_2()
    executar_cenario_3()