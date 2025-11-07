from fases import simular_preparacao

for _ in range(5):
    tempo, custo = simular_preparacao(10, 14, 20, 120000, 30000, 150000, 35000)
    print(f"Tempo: {tempo:.2f} dias | Custo: R${custo:,.2f}")
