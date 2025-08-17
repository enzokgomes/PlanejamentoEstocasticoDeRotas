from Classes.Scenario import Scenario
from Services.optimizer import run_model

import os
current_file_path = os.path.abspath(__file__)
current_folder_path = os.path.dirname(current_file_path)
if os.getcwd() != current_folder_path:
    os.chdir(current_folder_path)

px = [.35]
nt = [3500]
exchange_rate_variation = [0]
oil_price_variation = [0]
port_call_price_variation = [0]
intermodal_price_variation = [0]

num_years = 10
demand_variation_rate = .1

demand_variation = [0]
# demand_variation = [(1 + demand_variation_rate) ** year - 1 for year in range(num_years)]

freight_variation = [0]

scenarios = []

for _px in px:
    for _nt in nt:
        for _exchange_rate_variation in exchange_rate_variation:
            for _oil_price_variation in oil_price_variation:
                for _port_call_price_variation in port_call_price_variation:
                    for _intermodal_price_variation in intermodal_price_variation:
                        for _demand_variation in demand_variation:
                            for _freight_variation in freight_variation:
                                scenario = Scenario(px=_px, nt=_nt, exchange_rate_variation=_exchange_rate_variation, oil_price_variation=_oil_price_variation, port_call_price_variation=_port_call_price_variation, intermodal_price_variation=_intermodal_price_variation, demand_variation=_demand_variation, freight_variation=_freight_variation)
                                scenarios.append(scenario)

file_name = f'Input/Dados.xlsx'

for scenario in scenarios:
    output_path = f'Output/{scenario.name}.xlsx'
    run_model(scenario=scenario, descricao_cenario=scenario.description, file_name=file_name, output_path=output_path)
