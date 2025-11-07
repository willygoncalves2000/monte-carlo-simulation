import matplotlib.pyplot as plt
import numpy as np
from distribuicoes import (
    rand_uniform, rand_normal, rand_lognormal,
    rand_beta, rand_pert, rand_bernoulli
)

# ==============================================
# CONFIGURAÇÕES
# ==============================================
N = 1_000_000  # número de amostras
bins = 50      # número de barras do histograma

# ==============================================
# 1. UNIFORME
# ==============================================
samples_custom = [rand_uniform() for _ in range(N)]
samples_np = np.random.uniform(0, 1, N)

plt.figure(figsize=(10,4))
plt.hist(samples_custom, bins=bins, alpha=0.6, label="Custom", color="steelblue", density=True)
plt.hist(samples_np, bins=bins, alpha=0.5, label="Numpy", color="orange", density=True)
plt.title("Distribuição Uniforme U(0,1)")
plt.legend()
plt.show()


# ==============================================
# 2. NORMAL(0,1)
# ==============================================
samples_custom = [rand_normal(0, 1) for _ in range(N)]
samples_np = np.random.normal(0, 1, N)

plt.figure(figsize=(10,4))
plt.hist(samples_custom, bins=bins, alpha=0.6, label="Custom", color="steelblue", density=True)
plt.hist(samples_np, bins=bins, alpha=0.5, label="Numpy", color="orange", density=True)
plt.title("Distribuição Normal(0,1)")
plt.legend()
plt.show()


# ==============================================
# 3. LOGNORMAL(0, 0.25)
# ==============================================
samples_custom = [rand_lognormal(0, 0.25) for _ in range(N)]
samples_np = np.random.lognormal(0, 0.25, N)

plt.figure(figsize=(10,4))
plt.hist(samples_custom, bins=bins, alpha=0.6, label="Custom", color="steelblue", density=True)
plt.hist(samples_np, bins=bins, alpha=0.5, label="Numpy", color="orange", density=True)
plt.title("Distribuição LogNormal(0, 0.25)")
plt.legend()
plt.show()


# ==============================================
# 4. BETA(2,5)
# ==============================================
samples_custom = [rand_beta(2, 5) for _ in range(N)]
samples_np = np.random.beta(2, 5, N)

plt.figure(figsize=(10,4))
plt.hist(samples_custom, bins=bins, alpha=0.6, label="Custom", color="steelblue", density=True)
plt.hist(samples_np, bins=bins, alpha=0.5, label="Numpy", color="orange", density=True)
plt.title("Distribuição Beta(2,5)")
plt.legend()
plt.show()


# ==============================================
# 5. PERT(10,14,20)
# ==============================================
# A versão PERT não existe no NumPy, mas podemos gerar uma equivalente:
# Beta transformada para [o,p]
def pert_numpy(o, m, p, lambd=4):
    alpha = 1 + lambd * (m - o) / (p - o)
    beta = 1 + lambd * (p - m) / (p - o)
    x = np.random.beta(alpha, beta, N)
    return o + (p - o) * x

samples_custom = [rand_pert(10, 14, 20) for _ in range(N)]
samples_np = pert_numpy(10, 14, 20)

plt.figure(figsize=(10,4))
plt.hist(samples_custom, bins=bins, alpha=0.6, label="Custom", color="steelblue", density=True)
plt.hist(samples_np, bins=bins, alpha=0.5, label="Numpy-equivalente", color="orange", density=True)
plt.title("Distribuição PERT(10,14,20)")
plt.legend()
plt.show()
