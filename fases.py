# ==========================================================
# MÓDULO: phases.py
# Simulação das fases da construção civil
# ==========================================================
# Depende de: distributions.py
# ==========================================================

from distribuicoes import (
    converter_lognormal, rand_pert, rand_lognormal, rand_normal, rand_bernoulli
)


# ----------------------------------------------------------
# 1. Preparação do Terreno
# ----------------------------------------------------------
def simular_preparacao(o1, m1, p1, muM1, sigmaM1, muL1, sigmaL1):
    """Simula a fase de preparação do terreno."""
    T1 = rand_pert(o1, m1, p1)  # duração da fase
    mu_ln, sigma_ln = converter_lognormal(muM1, sigmaM1)  # converte parâmetros da LogNormal
    CM1 = rand_lognormal(mu_ln, sigma_ln)  # custo de material da fase
    CMO1 = rand_normal(muL1, sigmaL1)  # custo de mão de obra da fase

    T_total = T1
    C_total = CM1 + CMO1
    return T_total, C_total


# ----------------------------------------------------------
# 2. Fundação
# ----------------------------------------------------------
def simular_fundacao(
    oA, mA, pA, muMA, sigmaMA, muLA, sigmaLA,
    oB, mB, pB, muMB, sigmaMB, muLB, sigmaLB,
    probA, probGeo, T_geo, C_geo
):
    """Simula a fase de fundação com terceirizada A/B e risco geológico."""
    # Escolha da empresa
    EF = rand_bernoulli(probA)

    if EF == 1: # Empresa A
        T2 = rand_pert(oA, mA, pA) # duração da fase
        mu_ln, sigma_ln = converter_lognormal(muMA, sigmaMA)  # converte parâmetros da LogNormal
        CM2 = rand_lognormal(mu_ln, sigma_ln) # custo de material da fase
        CMO2 = rand_normal(muLA, sigmaLA) # custo de mão de obra

    else: # Empresa B
        T2 = rand_pert(oB, mB, pB) # duração da fase
        mu_ln, sigma_ln = converter_lognormal(muMB, sigmaMB)  # converte parâmetros da LogNormal
        CM2 = rand_lognormal(mu_ln, sigma_ln) # custo de material da fase
        CMO2 = rand_normal(muLB, sigmaLB) # custo de mão de obra
    
    # Evento geológico
    G = rand_bernoulli(probGeo)
    if G == 1:
        T_total = T2 + T_geo
        C_total = CM2 + CMO2 + C_geo
    else:
        T_total = T2
        C_total = CM2 + CMO2
    return T_total, C_total


# ----------------------------------------------------------
# 3. Laje
# ----------------------------------------------------------
def simular_laje(o3, m3, p3, muM3, sigmaM3, muL3, sigmaL3):
    """Simula a fase da laje."""
    T3 = rand_pert(o3, m3, p3)  # duração da fase
    mu_ln_M3, sigma_ln_M3 = converter_lognormal(muL3, sigmaL3)  # converte parâmetros da LogNormal
    CM3 = rand_lognormal(mu_ln_M3, sigma_ln_M3)  # custo de material da fase
    CMO3 = rand_normal(muL3, sigmaL3)  # custo de mão de obra da fase

    T_total = T3
    C_total = CM3 + CMO3
    return T_total, C_total

# ----------------------------------------------------------
# 4. Alvenaria
# ----------------------------------------------------------
def simular_alvenaria(o4, m4, p4, muM4, sigmaM4, muL4, sigmaL4, pR, C_retrabalho, T_retrabalho):
    """Simula a fase de alvenaria (com risco de retrabalho)."""
    T4 = rand_pert(o4, m4, p4)  # duração da fase
    mu_ln, sigma_ln = converter_lognormal(muL4, sigmaL4)  # converte parâmetros da LogNormal
    CM4 = rand_lognormal(mu_ln, sigma_ln)  # custo de material da fase
    CMO4 = rand_normal(muM4, sigmaM4)  # custo de mão de obra da fase

    # Sorteia evento de retrabalho
    R = rand_bernoulli(pR)

    if R == 1:
        T_total = T4 + T_retrabalho
        C_total = CM4 + CMO4 + C_retrabalho
    else:
        T_total = T4
        C_total = CM4 + CMO4

    return T_total, C_total

# ----------------------------------------------------------
# 5. Acabamento Interno
# ----------------------------------------------------------
def simular_acabamento(o5, m5, p5, muM5, sigmaM5, muL5, sigmaL5):
    """Simula a fase de acabamento interno."""
    T5 = rand_pert(o5, m5, p5)  # duração da fase
    mu_ln, sigma_ln = converter_lognormal(muM5, sigmaM5)  # converte parâmetros da LogNormal
    CM5 = rand_lognormal(mu_ln, sigma_ln)  # custo de material da fase
    CMO5 = rand_normal(muL5, sigmaL5)  # custo de mão de obra da fase

    T_total = T5
    C_total = CM5 + CMO5
    return T_total, C_total

# ----------------------------------------------------------
# 6. Pintura Externa
# ----------------------------------------------------------
def simular_pintura(
    pEP, pW,
    # Empresa A
    muMA, sigmaMA, muLA, sigmaLA,
    oA_bom, mA_bom, pA_bom,
    oA_chuva, mA_chuva, pA_chuva,
    # Empresa B
    muMB, sigmaMB, muLB, sigmaLB,
    oB_bom, mB_bom, pB_bom,
    oB_chuva, mB_chuva, pB_chuva
):
    """Simula a fase de pintura externa (empresa A/B + condição climática)."""
    EP = rand_bernoulli(pEP)  # Escolha da empresa
    W = rand_bernoulli(pW)    # Condição climática

    if EP == 1: # Empresa A
        mu_ln, sigma_ln = converter_lognormal(muMA, sigmaMA)  # converte parâmetros da LogNormal
        CM6 = rand_lognormal(mu_ln, sigma_ln)  # custo de material da fase
        CMO6 = rand_normal(muLA, sigmaLA)  # custo de mão de obra da fase
        if W == 1: # Dia de chuva
            T6 = rand_pert(oA_chuva, mA_chuva, pA_chuva)  # duração da fase
        else: # Dia bom
            T6 = rand_pert(oA_bom, mA_bom, pA_bom)  # duração da fase
    else: # Empresa B
        mu_ln, sigma_ln = converter_lognormal(muMB, sigmaMB)  # converte parâmetros da LogNormal
        CM6 = rand_lognormal(mu_ln, sigma_ln)  # custo de material da fase
        CMO6 = rand_normal(muLB, sigmaLB)  # custo de mão de obra da fase
        if W == 1: # Dia de chuva
            T6 = rand_pert(oB_chuva, mB_chuva, pB_chuva)  # duração da fase
        else: # Dia bom
            T6 = rand_pert(oB_bom, mB_bom, pB_bom)  # duração da fase

    T_total = T6
    C_total = CM6 + CMO6
    return T_total, C_total