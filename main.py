from gurobipy import Model, GRB
from Services.read_data import Dados

# Inicialização da classe Dados
file_name = 'Dados\Modelo.xlsx'  # Substitua pelo nome do seu arquivo
dados = Dados(file_name)

# Criar o modelo
model = Model("Modelo de Otimização de Cabotagem")

# Definir variáveis de decisão (Exemplo, ajuste conforme seu modelo)
X = model.addVars(dados.DF.index, vtype=GRB.CONTINUOUS, name="X")

# Função objetivo
model.setObjective(sum(dados.RF.loc[i] * X[i] for i in dados.RF.index), GRB.MAXIMIZE)

# Restrições (Exemplo, ajuste conforme seu modelo)
for i in dados.DF.index:
    model.addConstr(X[i] <= dados.DF.loc[i], f"Demanda_{i}")

# Exemplo de uma restrição adicional
for i in dados.CF.index:
    model.addConstr(sum(X[j] * dados.WF.loc[j] for j in dados.WF.index if j[:3] == i[:3]) <= dados.H.loc[i], f"Peso_{i}")

# Otimizar o modelo
model.optimize()

# Imprimir os resultados
if model.status == GRB.OPTIMAL:
    for v in model.getVars():
        print(f'{v.varName}: {v.x}')
    print(f'Obj: {model.objVal}')
else:
    print('No optimal solution found.')

