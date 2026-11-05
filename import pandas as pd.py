import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

arquivo = r"C:\Users\Santech\Desktop\Meg\Meg.xlsx"

# Métodos matemáticos que vamos testar
def metodo_progressao_aritmetica(seq):
    difs = np.diff(seq)
    if np.allclose(difs, difs[0]):
        return True, seq[-1] + difs[0]
    return False, None

def metodo_progressao_geometrica(seq):
    if np.any(np.array(seq) == 0):
        return False, None
    razoes = np.array(seq[1:]) / np.array(seq[:-1])
    if np.allclose(razoes, razoes[0]):
        return True, seq[-1] * razoes[0]
    return False, None

def metodo_regressao_linear(seq):
    X = np.arange(len(seq)).reshape(-1,1)
    y = np.array(seq)
    modelo = LinearRegression()
    modelo.fit(X,y)
    prox = modelo.predict([[len(seq)]])[0]
    return True, float(prox)

def metodo_regressao_polinomial(seq, grau=2):
    X = np.arange(len(seq)).reshape(-1,1)
    y = np.array(seq)
    poly = PolynomialFeatures(grau)
    X_poly = poly.fit_transform(X)
    modelo = LinearRegression()
    modelo.fit(X_poly, y)
    prox = modelo.predict(poly.transform([[len(seq)]]))[0]
    return True, float(prox)

def metodo_media(seq):
    return True, float(np.mean(seq))

def metodo_mediana(seq):
    return True, float(np.median(seq))


# Função geral para testar métodos
def descobrir_melhor_metodo(seq):
    metodos = {
        "Progressão Aritmética": metodo_progressao_aritmetica,
        "Progressão Geométrica": metodo_progressao_geometrica,
        "Regressão Linear": metodo_regressao_linear,
        "Regressão Polinomial Grau 2": metodo_regressao_polinomial,
        "Média": metodo_media,
        "Mediana": metodo_mediana
    }

    melhor_metodo = None
    melhor_erro = float('inf')
    melhor_previsao = None

    seq = np.array(seq).astype(float)

    for nome, func in metodos.items():
        ok, previsao = func(seq)
        if not ok:
            continue
        
        # erro = diferença entre valores reais e ajustados pelo modelo
        if nome == "Progressão Aritmética":
            modelo = np.arange(len(seq)) * (seq[1]-seq[0]) + seq[0]
        elif nome == "Progressão Geométrica":
            modelo = seq[0] * (seq[1]/seq[0]) ** np.arange(len(seq))
        elif nome == "Média":
            modelo = np.ones_like(seq) * np.mean(seq)
        elif nome == "Mediana":
            modelo = np.ones_like(seq) * np.median(seq)
        elif nome == "Regressão Linear":
            X = np.arange(len(seq)).reshape(-1,1)
            lr = LinearRegression().fit(X, seq)
            modelo = lr.predict(X)
        else:  # polinomial
            X = np.arange(len(seq)).reshape(-1,1)
            poly = PolynomialFeatures(2)
            Xp = poly.fit_transform(X)
            lr = LinearRegression().fit(Xp, seq)
            modelo = lr.predict(Xp)

        erro = np.mean((seq - modelo)**2)

        if erro < melhor_erro:
            melhor_erro = erro
            melhor_metodo = nome
            melhor_previsao = previsao

    return melhor_metodo, melhor_previsao


# === PROCESSAR TODAS AS ABAS ===
todas_abas = pd.read_excel(arquivo, sheet_name=None)

print("\n===== RESULTADOS =====\n")

for nome_aba, df in todas_abas.items():
    print(f"\n=== ABA: {nome_aba} ===\n")

    # Filtra somente valores numéricos
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.dropna(how="all", axis=1)
    df = df.dropna(how="all", axis=0)

    for idx, linha in df.iterrows():
        seq = linha.dropna().tolist()
        if len(seq) < 3:
            continue

        metodo, previsao = descobrir_melhor_metodo(seq)

        print(f"Linha {idx+1}: Melhor método = {metodo} → Próximo número previsto = {previsao:.2f}")