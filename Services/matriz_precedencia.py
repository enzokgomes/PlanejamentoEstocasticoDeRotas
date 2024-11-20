import pandas as pd

def gerar_matriz_precedencia(NB, SB):
    # Combina os portos de NB e SB
    ports = NB + SB
    matriz_ordem = pd.DataFrame(ports, index=range(1, len(ports) + 1), columns=['Porto'])

    # Mapear os portos para números
    num_portos = pd.DataFrame(list(set(NB + SB)), index=list(set(NB + SB)), columns=['Porto'])

    # Configurar índices e inicializar a matriz
    P = range(1, len(matriz_ordem) + 1)
    I = range(1, len(matriz_ordem.drop_duplicates()) + 1)
    J = range(1, len(matriz_ordem.drop_duplicates()) + 1)

    index = pd.MultiIndex.from_product([P, I, J], names=["P", "I", "J"])
    M = pd.DataFrame(0, index=index, columns=['M'])

    # Preencher a matriz para cada porto
    for p in P:
        p_port_name = matriz_ordem.loc[p].values[0]

        # Ignora último porto ou transição NB para SB
        if p == P[-1] or p == len(NB):
            continue

        elif p < len(NB):

            if p == 1:
                for i_port_name in SB[:-1]:
                    M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[p_port_name].values[0]] = 1
                for i_port_name in NB[1:]:
                    if not i_port_name in SB:
                        M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[p_port_name].values[0]] = 1

            idx_nb = NB.index(p_port_name)
            for i_port_name in NB[:idx_nb]:
                for j_port_name in NB[idx_nb:]:
                    M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[j_port_name].values[0]] = 1
                    if i_port_name == j_port_name:
                        print('Warning: NB')
                for j_port_name in SB:
                    if not ((i_port_name == j_port_name) or (j_port_name in NB)):
                        M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[j_port_name].values[0]] = 1
                for j_port_name in NB[:idx_nb]:
                    if not ((i_port_name == j_port_name) or (j_port_name in NB[idx_nb:]) or (j_port_name in SB)):
                        print("Nesse ex deveria ser 0 NB")
                        M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[j_port_name].values[0]] = 1
            for i_port_name in SB:
                for j_port_name in NB:
                    if i_port_name in NB:
                        condition = j_port_name in NB[NB.index(i_port_name):]
                    else:
                        condition = False
                    if (j_port_name in SB[SB.index(i_port_name):] or condition) or i_port_name == j_port_name:
                        continue
                    M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[j_port_name].values[0]] = 1


        elif p < (len(NB) + len(SB)):

            if p == len(NB) + 1:
                for i_port_name in NB[:-1]:
                    M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[p_port_name].values[0]] = 1
                for i_port_name in SB[1:]:
                    if not i_port_name in NB:
                        M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[p_port_name].values[0]] = 1

            idx_sb = SB.index(p_port_name)
            for i_port_name in SB[:idx_sb]:
                for j_port_name in SB[idx_sb:]:
                    M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[j_port_name].values[0]] = 1
                    if i_port_name == j_port_name:
                        print('Warning: SB')
                for j_port_name in NB:
                    if not ((i_port_name == j_port_name) or (j_port_name in SB)):
                        M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[j_port_name].values[0]] = 1
                for j_port_name in SB[:idx_sb]:
                    if not ((i_port_name == j_port_name) or (j_port_name in SB[idx_nb:]) or (j_port_name in NB)):
                        print("Nesse ex deveria ser 0 SB")
                        M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[j_port_name].values[0]] = 1
            for i_port_name in NB:
                for j_port_name in SB:
                    if i_port_name in SB:
                        condition = j_port_name in SB[SB.index(i_port_name):]
                    else:
                        condition = False
                    if (j_port_name in NB[NB.index(i_port_name):] or condition) or i_port_name == j_port_name:
                        continue
                    M.loc[p, num_portos.loc[i_port_name].values[0], num_portos.loc[j_port_name].values[0]] = 1

    return M
