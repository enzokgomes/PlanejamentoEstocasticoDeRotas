from gurobipy import Model
from Services.read_data import Dados
from Services.model_builder import data_processing, variable_setup, constraints, objective
from Services import exporter
from Services.exporter import export_results
from Classes.Scenario import Scenario

def run_model(scenario: Scenario, descricao_cenario, file_name, output_path):
    # Carregar dados
    dados = Dados(file_name)

    # Pré-processamento
    data_processing.preprocess_data(dados, scenario)

    # Cenário
    print(scenario.description)

    # Criação do modelo
    model = Model("Modelo de Otimização de Cabotagem")

    # Definir variáveis
    vars = variable_setup.setup_variables(model, dados)

    # Adicionar restrições
    constraints.add_constraints(model=model, dados=dados, vars=vars)

    # Definir função objetivo
    objective.set_objective(model=model, dados=dados, vars=vars)

    # Otimizar
    model.optimize()

    # Pós-processamento
    if model.status == 2:  # GRB.OPTIMAL
        print(f"Solução ótima encontrada com objetivo: {model.objVal}")
    else:
        print("Não foi possível encontrar uma solução ótima.")
    
    export_results(dados=dados, vars=vars, cenario=scenario.name, descricao_cenario=scenario.description, output_path=output_path)

    return model, dados, vars

# cenario = 'CEN01'
# descricao_cenario = 'Cenário 01'

# # Inicialização da classe Dados
# file_name = f'Input/Modelo {cenario}.xlsx'
# output_path = f'Output/{cenario}.xlsx'
# run_model(scenario=cenario, descricao_cenario=descricao_cenario, file_name=file_name, output_path=output_path)
