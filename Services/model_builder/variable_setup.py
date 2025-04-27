from gurobipy import GRB

def setup_variables(model, dados):

    # Variáveis de decisão
    CT = model.addVar(vtype=GRB.CONTINUOUS, name="CT", lb=0, ub=1)  # Margem de contribuição

    FF = model.addVars(dados.P, dados.P, dados.K, dados.C, dados.T, vtype=GRB.CONTINUOUS, name="FF")  # Contêineres cheios embarcados
    FE = model.addVars(dados.P, dados.P, dados.K, dados.T, vtype=GRB.CONTINUOUS, name="FE")  # Contêineres vazios embarcados

    E = model.addVars(dados.port_nums, dados.K, dados.T, vtype=GRB.CONTINUOUS, name="E")  # Estoque de contêineres vazios
    R = model.addVars(dados.P, dados.T, vtype=GRB.CONTINUOUS, name="R")  # Quantidade de TEU no navio

    # Variáveis auxiliares
    FF_port = model.addVars(dados.port_nums, dados.port_nums, dados.K, dados.C, dados.T, vtype=GRB.CONTINUOUS, name="FF_port")  # Contêineres cheios embarcados por porto
    FE_port = model.addVars(dados.port_nums, dados.port_nums, dados.K, dados.T, vtype=GRB.CONTINUOUS, name="FE_port")  # Contêineres vazios embarcados por porto

    RSF = model.addVars(dados.port_nums, dados.K, dados.T, vtype=GRB.CONTINUOUS, name="RSF")  # Contêineres vazios retornando
    RSE = model.addVars(dados.port_nums, dados.K, dados.T, vtype=GRB.CONTINUOUS, name="RSE")  # Contêineres vazios disponíveis
    RLF = model.addVars(dados.port_nums, dados.K, dados.T, vtype=GRB.CONTINUOUS, name="RLF")  # Contêineres vazios liberados para exportação
    RLE = model.addVars(dados.port_nums, dados.K, dados.T, vtype=GRB.CONTINUOUS, name="RLE")  # Contêineres vazios liberados para reposicionamento

    return {
        "CT": CT, "FF": FF, "FE": FE, "E": E, "R": R,
        "FF_port": FF_port, "FE_port": FE_port,
        "RSF": RSF, "RSE": RSE, "RLF": RLF, "RLE": RLE
    }
