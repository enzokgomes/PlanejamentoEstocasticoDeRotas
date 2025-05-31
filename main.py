from Classes.Scenario import Scenario
from Services.optimizer import run_model

import os
current_file_path = os.path.abspath(__file__)
current_folder_path = os.path.dirname(current_file_path)
if os.getcwd() != current_folder_path:
    os.chdir(current_folder_path)

scenarios = [
    Scenario(px=.4, nt=2000, exchange_rate_variation=0, oil_price_variation=0, 
             port_call_price_variation=0.1, intermodal_price_variation=0),

    Scenario(px=.4, nt=2000, exchange_rate_variation=0, oil_price_variation=0, 
             port_call_price_variation=0, intermodal_price_variation=0.1),

    Scenario(px=.4, nt=2000, exchange_rate_variation=0, oil_price_variation=0, 
             port_call_price_variation=-0.1, intermodal_price_variation=0),

    Scenario(px=.4, nt=2000, exchange_rate_variation=0, oil_price_variation=0, 
             port_call_price_variation=0, intermodal_price_variation=-0.1),

    Scenario(px=.35, nt=2000, exchange_rate_variation=0, oil_price_variation=0,
             port_call_price_variation=0, intermodal_price_variation=0),

    Scenario(px=.45, nt=2000, exchange_rate_variation=0, oil_price_variation=0,
             port_call_price_variation=0, intermodal_price_variation=0), # 0.5 px é 19.24% de mkt share

    Scenario(px=.40, nt=2500, exchange_rate_variation=0, oil_price_variation=0,
             port_call_price_variation=0, intermodal_price_variation=0),

    Scenario(px=.40, nt=3000, exchange_rate_variation=0, oil_price_variation=0,
             port_call_price_variation=0, intermodal_price_variation=0), # 0.4 px é 15.37% -> confirmar valores

    Scenario(px=.35, nt=3500, exchange_rate_variation=0, oil_price_variation=0,
             port_call_price_variation=0, intermodal_price_variation=0),

    Scenario(px=.45, nt=3500, exchange_rate_variation=0, oil_price_variation=0,
             port_call_price_variation=0, intermodal_price_variation=0),

]

file_name = f'Input/Dados.xlsx'

for scenario in scenarios:
    output_path = f'Output/{scenario.name}.xlsx'
    run_model(scenario=scenario, descricao_cenario=scenario.description, file_name=file_name, output_path=output_path)
