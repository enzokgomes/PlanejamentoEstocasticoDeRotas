def preprocess_data(dados, scenario):
    # Atualização de valores com variação de câmbio e petróleo
    dados.USD['Valor'] *= (1 + scenario.exchange_rate_variation)
    dados.USD['Valor'] = dados.USD['Valor'].round(2)
    dados.FUEL.loc[dados.FUEL['Combustível'] == 'VLSFO', 'Preço'] *= (1 + scenario.oil_price_variation)
    dados.FUEL.loc[dados.FUEL['Combustível'] == 'VLSFO', 'Preço'] = dados.FUEL.loc[dados.FUEL['Combustível'] == 'VLSFO', 'Preço'].round(2)

    # Definição de parâmetros-chave
    dados.NT = scenario.nt
    dados.PX['PX'] = scenario.px
    dados.ND = 22400 if dados.NT == 2000 else 39200
    dados.H['H'] = dados.ND
    dados.N = dados.NV * dados.NT / dados.TC
