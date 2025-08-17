from gurobipy import quicksum, GRB
from Services.utils import get_value

def set_objective(model, dados, vars):
    FF_port, FE_port, E = vars['FF_port'], vars['FE_port'], vars['E']

    # Defina a função objetivo
    model.setObjective(
        quicksum(
            (
                get_value(
                    dados.RF, 
                    (dados.RF['I'] == i) & 
                    (dados.RF['J'] == j) & 
                    (dados.RF['K'] == k) & 
                    (dados.RF['C'] == c) & 
                    (dados.RF['T'] == t), 
                    'RF'
                ) * FF_port[i, j, k, c, t] -

                get_value(
                    dados.CM, 
                    (dados.CM['C'] == c), 
                    'CM'
                ) * FF_port[i, j, k, c, t]
            )
            for i in dados.port_nums for j in dados.port_nums for k in dados.K for c in dados.C for t in dados.T
        ) +
        quicksum(
            (
                get_value(
                    dados.CF, 
                    (dados.CF['I'] == i) & 
                    (dados.CF['J'] == j) & 
                    (dados.CF['K'] == k), 
                    'CF'
                ) * FF_port[i, j, k, c, t]
            )
            for i in dados.port_nums for j in dados.port_nums for k in dados.K for c in dados.C_not_feeder for t in dados.T
        ) -
        quicksum(
            get_value(
                dados.CE, 
                (dados.CE['I'] == i) & 
                (dados.CE['J'] == j) & 
                (dados.CE['K'] == k), 
                'CE'
            ) * FE_port[i, j, k, t]
            for i in dados.port_nums for j in dados.port_nums for k in dados.K for t in dados.T
        ) -
        quicksum(
            get_value(
                dados.CS, 
                (dados.CS['K'] == k), 
                'CS'
            ) * E[j, k, t]
            for j in dados.port_nums for k in dados.K for t in dados.T
        ),
        GRB.MAXIMIZE
    )
