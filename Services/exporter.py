import pandas as pd
from Services.utils import aplicar_de_para, get_value
import numpy_financial as npf

def export_results(dados, vars, cenario, descricao_cenario, output_path):
    # Extrai as variáveis do modelo
    FF = vars['FF']
    FE = vars['FE']
    E = vars['E']
    R = vars['R']
    RSF = vars['RSF']
    RSE = vars['RSE']
    RLF = vars['RLF']
    RLE = vars['RLE']
    FF_port = vars['FF_port']
    FE_port = vars['FE_port']

    # Cria um dataframe pivotando os valores de FF em T, ou seja, cada linha contém os índices i, j, k, c e cada coluna é um período
    df_FF = pd.DataFrame([(i, j, k, c, t, FF[i, j, k, c, t].x) for i in dados.P for j in dados.P for k in dados.K for c in dados.C for t in dados.T], columns=['i', 'j', 'k', 'c', 't', 'value'])
    df_FF = df_FF.pivot_table(index=['i', 'j', 'k', 'c'], columns='t', values='value')

    # Cria um dataframe pivotando os valores de FE em T, ou seja, cada linha contém os índices i, j, k e cada coluna é um período
    df_FE = pd.DataFrame([(i, j, k, t, FE[i, j, k, t].x) for i in dados.P for j in dados.P for k in dados.K for t in dados.T], columns=['i', 'j', 'k', 't', 'value'])
    df_FE = df_FE.pivot_table(index=['i', 'j', 'k'], columns='t', values='value')

    # Cria um dataframe pivotando os valores de E em T, ou seja, cada linha contém os índices j, k e cada coluna é um período
    df_E = pd.DataFrame([(j, k, t, E[j, k, t].x) for j in dados.port_nums for k in dados.K for t in dados.T], columns=['j', 'k', 't', 'value'])
    df_E = df_E.pivot_table(index=['j', 'k'], columns='t', values='value')

    # Cria um dataframe pivotando os valores de R em T, ou seja, cada linha contém o índice p e cada coluna é um período
    df_R = pd.DataFrame([(p, t, R[p, t].x) for p in dados.P for t in dados.T], columns=['p', 't', 'value'])
    df_R = df_R.pivot_table(index='p', columns='t', values='value')

    # Cria um dataframe pivotando os valores de RSF em T, ou seja, cada linha contém os índices j, k e cada coluna é um período
    df_RSF = pd.DataFrame([(j, k, t, RSF[j, k, t].x) for j in dados.port_nums for k in dados.K for t in dados.T], columns=['j', 'k', 't', 'value'])
    df_RSF = df_RSF.pivot_table(index=['j', 'k'], columns='t', values='value')

    # Cria um dataframe pivotando os valores de RSE em T, ou seja, cada linha contém os índices j, k e cada coluna é um período
    df_RSE = pd.DataFrame([(j, k, t, RSE[j, k, t].x) for j in dados.port_nums for k in dados.K for t in dados.T], columns=['j', 'k', 't', 'value'])
    df_RSE = df_RSE.pivot_table(index=['j', 'k'], columns='t', values='value')

    # Cria um dataframe pivotando os valores de RLF em T, ou seja, cada linha contém os índices j, k e cada coluna é um período
    df_RLF = pd.DataFrame([(j, k, t, RLF[j, k, t].x) for j in dados.port_nums for k in dados.K for t in dados.T], columns=['j', 'k', 't', 'value'])
    df_RLF = df_RLF.pivot_table(index=['j', 'k'], columns='t', values='value')

    # Cria um dataframe pivotando os valores de RLE em T, ou seja, cada linha contém os índices j, k e cada coluna é um período
    df_RLE = pd.DataFrame([(j, k, t, RLE[j, k, t].x) for j in dados.port_nums for k in dados.K for t in dados.T], columns=['j', 'k', 't', 'value'])
    df_RLE = df_RLE.pivot_table(index=['j', 'k'], columns='t', values='value')

    #Cria um dataframe pivotando os valores de FF_port em T, ou seja, cada linha contém os índices i, j, k, c e cada coluna é um período
    df_FF_port = pd.DataFrame([(i, j, k, c, t, FF_port[i, j, k, c, t].x) for i in dados.port_nums for j in dados.port_nums for k in dados.K for c in dados.C for t in dados.T], columns=['i', 'j', 'k', 'c', 't', 'value'])
    df_FF_port = df_FF_port.pivot_table(index=['i', 'j', 'k', 'c'], columns='t', values='value')

    #Cria um dataframe pivotando os valores de FE_port em T, ou seja, cada linha contém os índices i, j, k e cada coluna é um período
    df_FE_port = pd.DataFrame([(i, j, k, t, FE_port[i, j, k, t].x) for i in dados.port_nums for j in dados.port_nums for k in dados.K for t in dados.T], columns=['i', 'j', 'k', 't', 'value'])
    df_FE_port = df_FE_port.pivot_table(index=['i', 'j', 'k'], columns='t', values='value')

    # Cria um DataFrame para armazenar os TM de embarque e desembarque de contêineres para cada porto e período
    df_TM_F = pd.DataFrame(columns=['I', 'T', 'EMB_FF' 'TM_EMB_FF', 'EMB_FE',  'TM_EMB_FE', 'DES_FF' 'TM_DES_FF',  'DES_FE', 'TM_DES_FE', 'TM'], 
                        index=pd.MultiIndex.from_product([dados.T, dados.P]))

    for t in dados.T:
        for p in dados.P:
            i_porto = dados.ordem.loc[p].values[0]
            tm_i = dados.TM[(dados.TM['I'] == i_porto)]['TM'].values[0]
            embarque_FF = sum(FF[p, j, k, c, t].x for j in dados.P for k in dados.K for c in dados.C) / dados.NV
            embarque_FE = sum(FE[p, j, k, t].x for j in dados.P for k in dados.K) / dados.NV
            desembarque_FF = sum(FF[j, p, k, c, t].x for j in dados.P for k in dados.K for c in dados.C) / dados.NV
            desembarque_FE = sum(FE[j, p, k, t].x for j in dados.P for k in dados.K) / dados.NV

            df_TM_F.loc[(t, p), 'I'] = i_porto
            df_TM_F.loc[(t, p), 'T'] = t

            df_TM_F.loc[(t, p), 'EMB_FF'] = embarque_FF
            df_TM_F.loc[(t, p), 'EMB_FE'] = embarque_FE
            df_TM_F.loc[(t, p), 'DES_FF'] = desembarque_FF
            df_TM_F.loc[(t, p), 'DES_FE'] = desembarque_FE

            df_TM_F.loc[(t, p), 'TM_EMB_FF'] = embarque_FF * tm_i
            df_TM_F.loc[(t, p), 'TM_EMB_FE'] = embarque_FE * tm_i
            df_TM_F.loc[(t, p), 'TM_DES_FF'] = desembarque_FF * tm_i
            df_TM_F.loc[(t, p), 'TM_DES_FE'] = desembarque_FE * tm_i
            df_TM_F.loc[(t, p), 'TM'] = (embarque_FF + embarque_FE + desembarque_FF + desembarque_FE) * tm_i

    #Cria um DataFrame para armazenar a velocidade de serviço para cada período
    df_vs_tempos = pd.DataFrame(columns=['Tempo de movimentacao', 'Tempo operacional', 'Tempo de Viagem','VS'], index=dados.T)

    sum_to = sum(dados.ordem.loc[dados.ordem['IdPorto'] == i]['TO'].values[0] for i in 
                (dados.NB[:-1] + dados.SB[:-1]))

    distancia_viagem = dados.ordem['DP'].sum()

    print(f"Distância total da viagem: {distancia_viagem}")
    print()

    for t in dados.T:
        sum_tm = sum(df_TM_F.loc[(t, p), 'TM'] for p in dados.P)
        
        sum_tm_to = sum_tm + sum_to
        
        print(f"Tempo de movimentação no período {t}: {sum_tm:.2f} dias")

        print(f"Tempo operacional no período {t}: {sum_to:.2f} dias")

        tempo_viagem = 28 - sum_tm_to

        print(f"Tempo de viagem no período {t}: {tempo_viagem:.2f} dias")

        vs = distancia_viagem / (tempo_viagem * 24)

        df_vs_tempos.loc[t, 'Tempo de movimentacao'] = sum_tm
        df_vs_tempos.loc[t, 'Tempo operacional'] = sum_to
        df_vs_tempos.loc[t, 'Tempo de Viagem'] = tempo_viagem
        df_vs_tempos.loc[t, 'VS'] = vs

        print(f"Velocidade de serviço no período {t}: {vs:.2f} nós")

        print()

    # Obtém o valor em dados.CSC['NT'] mais próxima de dados.NT
    vessel_nt = dados.CSC['NT'].iloc[(dados.CSC['NT'] - dados.NT).abs().argsort()[:1]].values[0]

    CSC_ports = dados.NB[:-1] + dados.SB[:-1]
    CSC = 0
    for port in CSC_ports:
        CSC += dados.CSC[(dados.CSC['I'] == port) & (dados.CSC['NT'] == vessel_nt)]['CSC'].values[0]

    CSC *= dados.NV

    custo_diario_afretamento = dados.CV[dados.CV['NT'] == vessel_nt]['CV'].values[0] * dados.USD['Valor'].values[0] * dados.NV
    custo_mensal_afretamento = custo_diario_afretamento * 31
    custo_anual_afretamento = custo_diario_afretamento * 12

    # Cria o dataframe de custo VLSFO para cada período
    df_custo_VLSFO = pd.DataFrame(columns=['Custo VLSFO'], index=dados.T)

    for t in dados.T:
        df_custo_VLSFO.loc[t, 'Custo VLSFO'] = (0.006754*df_vs_tempos.loc[t, 'VS']**3 +37.23) * df_vs_tempos.loc[t, 'Tempo de Viagem'] * dados.FUEL[dados.FUEL['Combustível'] == 'VLSFO']['Preço'].values[0] * dados.USD['Valor'].values[0] * dados.NV
        
    # Cria o dataframe de custo MDO para cada período
    df_custo_MDO = pd.DataFrame(columns=['Custo MDO'], index=dados.T)

    consumo_viagem = dados.MC[dados.MC['MDO Consumption'] == 'Sea']['t/day'].values[0]
    consumo_porto = dados.MC[dados.MC['MDO Consumption'] == 'Port']['t/day'].values[0]

    for t in dados.T:
        tempo_movimentacao = df_vs_tempos.loc[t, 'Tempo de movimentacao']
        tempo_operacional = df_vs_tempos.loc[t, 'Tempo operacional']
        tempo_viagem = df_vs_tempos.loc[t, 'Tempo de Viagem']

        consumo_total = (tempo_movimentacao * consumo_porto + tempo_operacional * consumo_porto + tempo_viagem * consumo_viagem) * dados.NV

        df_custo_MDO.loc[t, 'Custo MDO'] = consumo_total * dados.FUEL[dados.FUEL['Combustível'] == 'MDO']['Preço'].values[0] * dados.USD['Valor'].values[0]

    custo_intermodal = pd.Series(0, index=dados.T)
    # frete_rodoviario_por_km = 5.67 # em reais, mas levar pra planilha de dados
    # custo_carga_descarga = 496.50
    # fator_extra_intermodal = 0.3

    frete_rodoviario_por_km = dados.CI['Valor'].values[0]
    custo_carga_descarga = dados.CI['Valor'].values[1]
    fator_extra_intermodal = dados.CI['Valor'].values[2]

    for i in df_FF_port.index.levels[0]:
        for j in df_FF_port.index.levels[1]:
            if i == j:
                continue
            else:
                # Dist deve ser dist porto - capital...
                dist = (dados.DC[dados.DC['Porto'] == i]['Distância Capital'].values[0] + dados.DC[dados.DC['Porto'] == j]['Distância Capital'].values[0] * 2)
                custo_unitario = (dist * frete_rodoviario_por_km + custo_carga_descarga) * (1 + fator_extra_intermodal)
                demanda = df_FF_port.loc[i, j, slice(None), slice(None)].sum()
                custo_total = demanda * custo_unitario
                custo_intermodal += custo_total

    # Cria o dataframe de custo de intermodal para cada período
    df_custo_intermodal = pd.DataFrame(columns=['Custo intermodal'], index=dados.T)

    for t in dados.T:
        df_custo_intermodal.loc[t, 'Custo intermodal'] = custo_intermodal[t]

    # Cria um dataframe para gerar o proforma da rota de cabotagem para o 1º período
    t = 6
    vs = df_vs_tempos.loc[t, 'VS']

    df_proforma = pd.DataFrame(index=dados.P)

    for p in dados.P:
        i_porto = dados.ordem.loc[p].values[0]
        nome_trecho_p = dados.De_Para_Trechos.loc[dados.De_Para_Trechos['Para.1'] == p].values[0][0]
        p_proximo = p + 1 if p < len(dados.P) else 1
        nome_trecho_p_proximo = dados.De_Para_Trechos.loc[dados.De_Para_Trechos['Para.1'] == p_proximo].values[0][0]
        i_proximo = dados.ordem.loc[p_proximo].values[0]
        p_anterior = p - 1 if p > 1 else len(dados.P)
        i_anterior = dados.ordem.loc[p_anterior].values[0]
        nome_trecho_p_anterior = dados.De_Para_Trechos.loc[dados.De_Para_Trechos['Para.1'] == p_anterior].values[0][0]
        
        tm_f = df_TM_F.loc[(t, p)]

        tm_ff_emb = tm_f['TM_EMB_FF']
        tm_fe_emb = tm_f['TM_EMB_FE']
        tm_ff_des = tm_f['TM_DES_FF']
        tm_fe_des = tm_f['TM_DES_FE']
        
        embarque_FF = tm_f['EMB_FF']
        desembarque_FF = tm_f['DES_FF']
        embarque_FE = tm_f['EMB_FE']
        desembarque_FE = tm_f['DES_FE']

        df_proforma.loc[p, 'Porto'] = nome_trecho_p
        df_proforma.loc[p, 'Proximo'] = nome_trecho_p_proximo
        df_proforma.loc[p, 'Velocidade'] = vs
        df_proforma.loc[p, 'Distancia'] = dados.ordem.loc[p, 'DP']
        df_proforma.loc[p, 'Tempo de viagem em mar'] = dados.ordem.loc[p, 'DP'] / (vs * 24)
        df_proforma.loc[p, 'Embarque cheios'] = embarque_FF
        df_proforma.loc[p, 'Tempo de embarque cheios'] = tm_ff_emb
        df_proforma.loc[p, 'Desembarque cheios'] = desembarque_FF
        df_proforma.loc[p, 'Tempo de desembarque cheios'] = tm_ff_des
        df_proforma.loc[p, 'Embarque vazios'] = embarque_FE
        df_proforma.loc[p, 'Tempo de embarque vazios'] = tm_fe_emb
        df_proforma.loc[p, 'Desembarque vazios'] = desembarque_FE
        df_proforma.loc[p, 'Tempo de desembarque vazios'] = tm_fe_des
        df_proforma.loc[p, 'Tempo total de movimentacao'] = tm_ff_emb + tm_fe_emb + tm_ff_des + tm_fe_des
        df_proforma.loc[p, 'Tempo operacional'] = dados.ordem.loc[dados.ordem['IdPorto'] == i_porto]['TO'].values[0]
        df_proforma.loc[p, 'Tempo total do trecho'] = df_proforma.loc[p, 'Tempo de viagem em mar'] + df_proforma.loc[p, 'Tempo total de movimentacao'] + df_proforma.loc[p, 'Tempo operacional']

        # Calcula a quantidade de TEUs transportados saindo de p
        df_proforma.loc[p, 'TEUs'] = R[p, t].x / dados.NV
        # Calcula a ocupação percentual do navio
        df_proforma.loc[p, 'Ocupacao'] = R[p, t].x / dados.NT / dados.NV * dados.TC

        # Calcula a receita do trecho (validado)

        receita_frete = sum(get_value(
                    dados.RF, 
                    (dados.RF['I'] == i_porto) & 
                    (dados.RF['J'] == dados.ordem.loc[j].values[0]) & 
                    (dados.RF['K'] == k) & 
                    (dados.RF['C'] == c) & 
                    (dados.RF['T'] == t), 
                    'RF'
                ) * FF[p, j, k, c, t].x for j in dados.P for k in dados.K for c in dados.C) / dados.NV

        df_proforma.loc[p, 'Receita'] = receita_frete

        # Custos de movimentação de contêineres no trecho (validado)
        custo_embarque_cheios = sum(FF[p, j, k, c, t].x * dados.CF[(dados.CF['I'] == i_porto) & (dados.CF['J'] == dados.ordem.loc[j].values[0]) & (dados.CF['K'] == k)]['CF'].values[0] for j in dados.P for k in dados.K for c in dados.C) / dados.NV
        
        df_proforma.loc[p, 'Custo de movimentação de cheios'] = custo_embarque_cheios

        custo_embarque_vazios = sum(FE[p, j, k, t].x * dados.CE[(dados.CE['I'] == i_porto) & (dados.CE['J'] == dados.ordem.loc[j].values[0]) & (dados.CE['K'] == k)]['CE'].values[0] for j in dados.P for k in dados.K) / dados.NV
        
        df_proforma.loc[p, 'Custo de movimentação de vazios'] = custo_embarque_vazios

        # Calcula o custo de vlsfo no trecho (validado)
        df_proforma.loc[p, 'Custo de VLSFO'] = (0.006754*vs**3 +37.23) * df_proforma.loc[p, 'Tempo de viagem em mar'] * dados.FUEL[dados.FUEL['Combustível'] == 'VLSFO']['Preço'].values[0] * dados.USD['Valor'].values[0]

        # Calcula o custo de mdo no trecho
        consumo_viagem_total = df_proforma.loc[p, 'Tempo de viagem em mar'] * consumo_viagem 
        consumo_porto_total = df_proforma.loc[p, 'Tempo total de movimentacao'] * consumo_porto + df_proforma.loc[p, 'Tempo operacional'] * consumo_porto

        df_proforma.loc[p, 'Custo de MDO viagem'] = consumo_viagem_total * dados.FUEL[dados.FUEL['Combustível'] == 'MDO']['Preço'].values[0] * dados.USD['Valor'].values[0]
        df_proforma.loc[p, 'Custo de MDO porto'] = consumo_porto_total * dados.FUEL[dados.FUEL['Combustível'] == 'MDO']['Preço'].values[0] * dados.USD['Valor'].values[0]

        # Calcula o custo de escala no trecho com base em dados.CSC e usando vessel_nt (validado)
        df_proforma.loc[p, 'Custo de escala'] = dados.CSC[(dados.CSC['I'] == i_porto) & (dados.CSC['NT'] == vessel_nt)]['CSC'].values[0] if i_porto != i_anterior else 0

        # Calcula o custo de intermodal no trecho (validado)
        custo_intermodal_trecho = 0
        for j in dados.P:
            if i_porto == dados.ordem.loc[j].values[0]:
                continue
            else:
                dist = (dados.DC[dados.DC['Porto'] == i_porto]['Distância Capital'].values[0] + dados.DC[dados.DC['Porto'] == dados.ordem.loc[j].values[0]]['Distância Capital'].values[0] * 2)
                custo_unitario = (dist * frete_rodoviario_por_km + custo_carga_descarga) * (1 + fator_extra_intermodal)
                demanda = sum(FF[p, j, k, c, t].x for k in dados.K for c in dados.C) / dados.NV
                custo_total = demanda * custo_unitario
                custo_intermodal_trecho += custo_total

        df_proforma.loc[p, 'Custo de intermodal'] = custo_intermodal_trecho

    # Calcula o fluxo de caixa da operação para cada período

    # Receita
    df_fluxo_caixa = pd.DataFrame(
        [
            sum(
                get_value(
                    dados.RF, 
                    (dados.RF['I'] == i) & 
                    (dados.RF['J'] == j) & 
                    (dados.RF['K'] == k) & 
                    (dados.RF['C'] == c) & 
                    (dados.RF['T'] == t), 
                    'RF'
                ) * FF_port[i, j, k, c, t].x
                for i in dados.port_nums for j in dados.port_nums for k in dados.K for c in dados.C
            )
            for t in dados.T
        ],
        columns=['Receita']
    )

    # Custo de movimentação de cheios
    df_fluxo_caixa['Custo de movimentação de cheios'] = [
        sum(
            get_value(
                dados.CF, 
                (dados.CF['I'] == i) & 
                (dados.CF['J'] == j) & 
                (dados.CF['K'] == k), 
                'CF'
            ) * FF_port[i, j, k, c, t].x
            for i in dados.port_nums for j in dados.port_nums for k in dados.K for c in dados.C
        )
        for t in dados.T
    ]

    # Custo de movimentação de vazios
    df_fluxo_caixa['Custo de movimentação de vazios'] = [
        sum(
            get_value(
                dados.CE, 
                (dados.CE['I'] == i) & 
                (dados.CE['J'] == j) & 
                (dados.CE['K'] == k), 
                'CE'
            ) * FE_port[i, j, k, t].x
            for i in dados.port_nums for j in dados.port_nums for k in dados.K
        )
        for t in dados.T
    ]

    # Custo de estoque
    df_fluxo_caixa['Custo de estoque'] = [
        sum(
            get_value(
                dados.CS, 
                (dados.CS['K'] == k), 
                'CS'
            ) * E[j, k, t].x    
            for j in dados.port_nums for k in dados.K
        )
        for t in dados.T
    ]

    # Custo do tipo de carga CM
    df_fluxo_caixa['Custo do tipo de carga'] = [
        sum(
            get_value(
                dados.CM, 
                (dados.CM['C'] == c), 
                'CM'
            ) * FF_port[i, j, k, c, t].x
            for i in dados.port_nums for j in dados.port_nums for k in dados.K for c in dados.C
        )
        for t in dados.T
    ]

    # Custo de escala csc
    df_fluxo_caixa['Custo de escala csc'] = [
        CSC
        for t in dados.T
    ]

    # Custo de intermodal
    df_fluxo_caixa['Custo de intermodal'] = [
        df_custo_intermodal.loc[t, 'Custo intermodal']
        for t in dados.T
    ]

    # Custo de VLSFO
    df_fluxo_caixa['Custo de VLSFO'] = [
        df_custo_VLSFO.loc[t, 'Custo VLSFO']
        for t in dados.T
    ]

    # Custo de MDO
    df_fluxo_caixa['Custo de MDO'] = [
        df_custo_MDO.loc[t, 'Custo MDO']
        for t in dados.T
    ]

    #Custo de afretamento
    df_fluxo_caixa['Custo de afretamento'] = custo_mensal_afretamento

    # Custo total
    df_fluxo_caixa['Custo'] = df_fluxo_caixa['Custo de movimentação de cheios'] + df_fluxo_caixa['Custo de movimentação de vazios'] + df_fluxo_caixa['Custo de estoque'] + df_fluxo_caixa['Custo do tipo de carga'] + df_fluxo_caixa['Custo de escala csc'] + df_fluxo_caixa['Custo de intermodal'] + df_fluxo_caixa['Custo de VLSFO'] + df_fluxo_caixa['Custo de MDO'] + df_fluxo_caixa['Custo de afretamento']

    # Resultado operacional
    df_fluxo_caixa['Resultado operacional'] = df_fluxo_caixa['Receita'] - df_fluxo_caixa['Custo']

    # Definição do investimento inicial (se houver)
    investimento_inicial = 0

    # Fluxo de Caixa Líquido
    fluxo_caixa_liquido = [-investimento_inicial] + list(df_fluxo_caixa['Resultado operacional'])

    # Recalcula a TIR
    tir = npf.irr(fluxo_caixa_liquido)

    print(f'Taxa Interna de Retorno: {tir * 100:.2f}%')

    # usa a função aplicar_de_para_seguro no datarame df_FF_port
    df_FF_port = aplicar_de_para(df_FF_port, dados.De_Para_Portos, ['i', 'j'])
    df_FF_port = aplicar_de_para(df_FF_port, dados.De_Para_K, ['k'])
    df_FF_port = aplicar_de_para(df_FF_port, dados.De_Para_C, ['c'])

    # usa a função aplicar_de_para_seguro no datarame df_FE_port
    df_FE_port = aplicar_de_para(df_FE_port, dados.De_Para_Portos, ['i', 'j'])
    df_FE_port = aplicar_de_para(df_FE_port, dados.De_Para_K, ['k'])

    # usa a função aplicar_de_para_seguro no datarame df_FF
    df_FF = aplicar_de_para(df_FF, dados.De_Para_Trechos, ['i', 'j'])
    df_FF = aplicar_de_para(df_FF, dados.De_Para_K, ['k'])
    df_FF = aplicar_de_para(df_FF, dados.De_Para_C, ['c'])

    # usa a função aplicar_de_para_seguro no datarame df_FE
    df_FE = aplicar_de_para(df_FE, dados.De_Para_Trechos, ['i', 'j'])
    df_FE = aplicar_de_para(df_FE, dados.De_Para_K, ['k'])

    # usa a função aplicar_de_para_seguro no datarame df_E
    df_E = aplicar_de_para(df_E, dados.De_Para_Portos, ['j'])
    df_E = aplicar_de_para(df_E, dados.De_Para_K, ['k'])

    # usa a função aplicar_de_para_seguro no datarame df_R
    df_R = aplicar_de_para(df_R, dados.De_Para_Trechos, ['p'])

    # usa a função aplicar_de_para_seguro no datarame df_RSF
    df_RSF = aplicar_de_para(df_RSF, dados.De_Para_Portos, ['j'])
    df_RSF = aplicar_de_para(df_RSF, dados.De_Para_K, ['k'])

    # usa a função aplicar_de_para_seguro no datarame df_RSE
    df_RSE = aplicar_de_para(df_RSE, dados.De_Para_Portos, ['j'])
    df_RSE = aplicar_de_para(df_RSE, dados.De_Para_K, ['k'])

    # usa a função aplicar_de_para_seguro no datarame df_RLF
    df_RLF = aplicar_de_para(df_RLF, dados.De_Para_Portos, ['j'])
    df_RLF = aplicar_de_para(df_RLF, dados.De_Para_K, ['k'])

    # usa a função aplicar_de_para_seguro no datarame df_RLE
    df_RLE = aplicar_de_para(df_RLE, dados.De_Para_Portos, ['j'])
    df_RLE = aplicar_de_para(df_RLE, dados.De_Para_K, ['k'])

    demanda_total = dados.demanda_total
    sum_ff = sum(FF[i, j, k, c, t].x for i in dados.P for j in dados.P for k in dados.K for c in dados.C for t in dados.T)

    print(f"Demanda total: {demanda_total}")
    print(f"Demanda total atendida: {sum_ff}")
    print(f"Demanda total atendida em %: {sum_ff / demanda_total:.2%}")

    # Exporta tudo para um arquivo excel, colocando a descrição do cenário na primeira aba
    with pd.ExcelWriter(output_path) as writer:
        pd.DataFrame([descricao_cenario], columns=['Descrição do cenário']).to_excel(writer, sheet_name='Descrição do cenário')

        # Adiciona na 1ª aba o market share relativo a demanda total
        pd.DataFrame([['Demanda total', demanda_total], ['Demanda atendida', sum_ff], ['Market share', sum_ff / demanda_total]], columns=['Descrição', 'Valor']).to_excel(writer, sheet_name='Descrição do cenário', startrow=2, index=False)

        #Exporta o proforma da rota de cabotagem
        df_proforma.to_excel(writer, sheet_name='Proforma')

        #Exporta o fluxo de caixa, adicionando mais uma linha somente com o investimento inicial, a TIR e o valor presente líquido
        df_fluxo_caixa.to_excel(writer, sheet_name='Fluxo de Caixa')
        pd.DataFrame([['Investimento inicial', investimento_inicial], ['TIR', tir], ['VPL', npf.npv(tir, fluxo_caixa_liquido)]], columns=['Período', 'Valor']).to_excel(writer, sheet_name='Fluxo de Caixa', startrow=len(df_fluxo_caixa) + 2, index=False)
        
        df_FF.to_excel(writer, sheet_name='FF')
        df_FE.to_excel(writer, sheet_name='FE')
        df_E.to_excel(writer, sheet_name='E')
        df_R.to_excel(writer, sheet_name='R')
        df_RSF.to_excel(writer, sheet_name='RSF')
        df_RSE.to_excel(writer, sheet_name='RSE')
        df_RLF.to_excel(writer, sheet_name='RLF')
        df_RLE.to_excel(writer, sheet_name='RLE')
        df_FF_port.to_excel(writer, sheet_name='FF_port')
        df_FE_port.to_excel(writer, sheet_name='FE_port')