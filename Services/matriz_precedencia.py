import pandas as pd

def criar_matriz_ordem(ports):
    return pd.DataFrame(ports, index=range(1, len(ports) + 1), columns=['Porto'])

def criar_num_portos():
    return pd.DataFrame([1, 2, 3, 4], index=['SSP', 'SSZ', 'SUA', 'MAO'], columns=['Porto'])

def inicializar_matriz(P, I, J):
    index = pd.MultiIndex.from_product([P, I, J], names=["P", "I", "J"])
    return pd.DataFrame(0, index=index, columns=['M'])

def preencher_matriz_por_porto(M, p, num_portos, NB, SB, p_port_name):
    idx_nb = NB.index(p_port_name) if p_port_name in NB else None
    idx_sb = SB.index(p_port_name) if p_port_name in SB else None
    
    # Função para atualizar a matriz baseada na precedência entre os portos
    def atualizar_matriz(i_port_name, j_port_name):
        M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[j_port_name].values[0]] = 1
    
    if p < len(NB):  # Se p estiver na primeira metade dos portos (NB)
        for i_port_name in NB[:idx_nb]:
            for j_port_name in NB[idx_nb:]:
                atualizar_matriz(i_port_name, j_port_name)
        for i_port_name in SB[:-1]:  # Preencher para portos da rota SB
            atualizar_matriz(i_port_name, p_port_name)

    elif p < (len(NB) + len(SB)):  # Se p estiver na segunda metade dos portos (SB)
        for i_port_name in SB[:idx_sb]:
            for j_port_name in SB[idx_sb:]:
                atualizar_matriz(i_port_name, j_port_name)
        for i_port_name in NB[:-1]:  # Preencher para portos da rota NB
            atualizar_matriz(i_port_name, p_port_name)

def criar_matriz_de_precedencia(NB, SB):
    ports = NB + SB
    matriz_ordem = criar_matriz_ordem(ports)
    num_portos = criar_num_portos()
    P = range(1, len(matriz_ordem) + 1)
    I = J = range(1, len(matriz_ordem.drop_duplicates()) + 1)
    M = inicializar_matriz(P, I, J)

    for p in P:
        p_port_name = matriz_ordem.loc[p].values[0]
        if p == P[-1] or p == len(NB):  # Ignorar último porto ou final da lista NB
            continue
        preencher_matriz_por_porto(M, p, num_portos, NB, SB, p_port_name)

    return M