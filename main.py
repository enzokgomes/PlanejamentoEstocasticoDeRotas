from Classes.Scenario import Scenario
from Services.optimizer import run_model

scenarios = [
    Scenario(px=.75, nt=3500, exchange_rate_variation=0, oil_price_variation=0),
]

file_name = f'Input\Dados.xlsx'

for scenario in scenarios:
    output_path = f'Output/{scenario.name}.xlsx'
    run_model(scenario=scenario, descricao_cenario=scenario.description, file_name=file_name, output_path=output_path)
