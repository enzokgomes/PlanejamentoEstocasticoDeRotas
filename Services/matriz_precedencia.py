import pandas as pd

def gerar_matriz_precedencia(NB, SB):
    # Combina os portos de NB e SB
    ports = NB + SB
    matriz_ordem = pd.DataFrame(ports, index=range(1, len(ports) + 1), columns=['Porto'])

    # Mapear os portos para números
    num_portos = pd.DataFrame(list(set(NB + SB)), index=list(set(NB + SB)), columns=['Porto'])

    # Configurar índices e inicializar a matriz
    P = range(1, len(matriz_ordem) + 1)
    I = P
    J = P

    index = pd.MultiIndex.from_product([P, I, J], names=["P", "I", "J"])
    M = pd.DataFrame(0, index=index, columns=['M'])

    # Preencher a matriz para cada porto
    for p in P:
        if p == 1 or p == len(NB) + 1:  # Primeiro de NB ou SB
            continue
        for i in range(1, p):
            if i < len(NB):
                for j in range(p, len(NB) + 1):
                    M.loc[p, i, j] = 1
            elif i > len(NB):
                for j in range(p, len(P) + 1):
                    M.loc[p, i, j] = 1
    return M