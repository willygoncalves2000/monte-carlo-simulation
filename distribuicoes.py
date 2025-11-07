import math
import time
seed_changeable = int(time.time() * 1000) % 2**32
seed_static = 123456789
# seed_static = 999

# ---------------------------
# 1. Gerador Uniforme (LCG)
# ---------------------------

class LCG:
    def __init__(self, seed = seed_static):
        self.a = 1664525
        self.c = 1013904223
        self.m = 2**32
        self.X = seed

    def rand(self):
        self.X  = (self.a * self.X + self.c) % self.m
        return self.X / self.m
    
lcg = LCG()

def rand_uniform():
    # Retorna um número aleatório uniforme U(0,1)
    return lcg.rand()

# ---------------------------
# 2. Bernoulli(p)
# --------------------------
def rand_bernoulli(p):
    # Retorna 1 com probabilidade p e 0 com probabilidade 1-p
    return 1 if rand_uniform() < p else 0

# ---------------------------
# 3. Normal(μ, σ) - Box-Muller
# --------------------------
def rand_normal(mu=0, sigma=1):
    # Gera número Normal(μ, σ) usando o método Box-Muller
    u1 = rand_uniform()
    u2 = rand_uniform()
    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return mu + sigma * z

# ---------------------------
# 4. LogNormal(μ, σ)
# ---------------------------
def rand_lognormal(mu, sigma):
    # Gera número LogNormal(μ, σ)
    x = rand_normal(mu, sigma)
    return math.exp(x)

def converter_lognormal(media, desvio):
    """Converte média e desvio reais em parâmetros μ_ln e σ_ln."""
    variancia = desvio ** 2
    mu_ln = math.log((media ** 2) / math.sqrt(variancia + media ** 2))
    sigma_ln = math.sqrt(math.log(1 + variancia / (media ** 2)))
    return mu_ln, sigma_ln

# ---------------------------
# 5. Gamma(k, θ=1) - Marsaglia & Tsang
# ---------------------------
def rand_gamma(k, theta=1.0):
    """Gera número Gamma(k, θ=1). Adaptado de Marsaglia & Tsang (2000)."""
    if k <= 0:
        raise ValueError("Parâmetro k deve ser positivo.")

    if k < 1:
        # Usa a transformação de Johnk para k < 1
        while True:
            u = rand_uniform()
            b = (math.e + k) / math.e
            p = b * u
            if p <= 1:
                x = p ** (1 / k)
            else:
                x = -math.log((b - p) / k)
            u2 = rand_uniform()
            if p <= 1:
                if u2 <= math.exp(-x):
                    return theta * x
            else:
                if u2 <= x ** (k - 1):
                    return theta * x
    else:
        d = k - 1/3
        c = 1 / math.sqrt(9 * d)
        while True:
            z = rand_normal()
            u = rand_uniform()
            v = (1 + c * z) ** 3
            if v > 0 and math.log(u) < 0.5 * z**2 + d - d * v + d * math.log(v):
                return theta * d * v


# ---------------------------
# 6. Beta(α, β)
# ---------------------------
def rand_beta(alpha, beta):
    """Gera número Beta(α, β) usando razão de gamas."""
    g1 = rand_gamma(alpha, 1)
    g2 = rand_gamma(beta, 1)
    return g1 / (g1 + g2)


# ---------------------------
# 7. PERT(o, m, p)
# ---------------------------
def rand_pert(o, m, p):
    """
    Gera número PERT(o, m, p).
    Baseado em Beta(α, β) com fator de suavização 4.
    """
    if not (o < m < p):
        raise ValueError("Deve-se ter o < m < p.")
    
    alpha = 1 + 4 * (m - o) / (p - o)
    beta = 1 + 4 * (p - m) / (p - o)
    x = rand_beta(alpha, beta)
    return o + (p - o) * x

# ==========================================================
# Teste rápido (executar para validar)
# ==========================================================
if __name__ == "__main__":
    print("Teste rápido das distribuições:\n")
    print("Uniforme:", [round(rand_uniform(), 3) for _ in range(5)])
    print("Bernoulli(p=0.3):", [rand_bernoulli(0.3) for _ in range(10)])
    print("Normal(0,1):", [round(rand_normal(), 3) for _ in range(5)])
    print("LogNormal(0,0.25):", [round(rand_lognormal(0, 0.25), 3) for _ in range(5)])
    print("Gamma(2):", [round(rand_gamma(2), 3) for _ in range(5)])
    print("Beta(2,5):", [round(rand_beta(2,5), 3) for _ in range(5)])
    print("PERT(10,14,20):", [round(rand_pert(10,14,20), 3) for _ in range(5)])

