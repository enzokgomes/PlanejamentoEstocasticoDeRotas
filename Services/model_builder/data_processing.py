def preprocess_data(dados, scenario):
    # Atualização de valores com variação de câmbio e petróleo
    dados.USD['Valor'] *= (1 + scenario.exchange_rate_variation)
    dados.USD['Valor'] = dados.USD['Valor'].round(2)
    dados.FUEL.loc[dados.FUEL['Combustível'] == 'VLSFO', 'Preço'] *= (1 + scenario.oil_price_variation)
    dados.FUEL.loc[dados.FUEL['Combustível'] == 'VLSFO', 'Preço'] = dados.FUEL.loc[dados.FUEL['Combustível'] == 'VLSFO', 'Preço'].round(2)

    dados.CSC['CSC'] *= (1 + scenario.port_call_price_variation)
    dados.CSC['CSC'] = dados.CSC['CSC'].round(0)

    dados.CI.iloc[0,1] *= (1+ scenario.intermodal_price_variation)

    # Definição de parâmetros-chave
    dados.NT = scenario.nt
    dados.PX['PX'] = scenario.px
    dados.ND = 22400 if dados.NT == 2000 else 39200
    dados.H['H'] = dados.ND
    dados.N = dados.NV * dados.NT / dados.TC

    # Atualizando a variação demanda
    dados.DF.update((x , y*(1+scenario.demand_variation))for x, y in dados.DF.items())
    dados.demanda_total *= (1+scenario.demand_variation)

    # Atualizando a variação no frete
    # dados.RF.loc[dados.RF['C'] == 1] *= (1 + scenario.freight_variation)
    dados.RF['RF'] *= (1 + scenario.freight_variation)

    # Atualizando dados de Slot Cost
    dados.RF.loc[(dados.RF['C'] == 2) & (dados.RF['K'].isin(dados.K_40pes))] = dados.slot_cost * (1 + 0.25) * 2
    dados.RF.loc[(dados.RF['C'] == 2) & ~(dados.RF['K'].isin(dados.K_40pes))] = dados.slot_cost * (1 + 0.25) * 1
    print(f"Slot Cost: R$ {dados.slot_cost:.2f}")

