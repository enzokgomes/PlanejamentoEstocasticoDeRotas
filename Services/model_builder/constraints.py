from gurobipy import quicksum

def add_constraints(model, dados, vars):
    enforce_forward_flow(model, vars, dados)
    enforce_relation_between_FF_FE_and_ports(model, vars, dados)
    enforce_carrier_participation_limits(model, vars, dados)
    enforce_precedence_matrix(model, vars, dados)               
    enforce_empty_container_balance(model, vars, dados)
    enforce_returned_containers_quantity(model, vars, dados)
    enforce_max_empty_containers_per_port(model, vars, dados)
    enforce_R_relationship(model, vars, dados)
    enforce_limit_Rp_t_to_N(model, vars, dados)
    enforce_deadweight_limit_in_ports(model, vars, dados)
    enforce_max_refrigerated_containers_on_ships(model, vars, dados)
    enforce_max_40ft_containers_on_ships(model, vars, dados)
    enforce_fleet_capacity_limit(model, vars, dados)
    print("All constraints added to the model.")

def enforce_forward_flow(model, vars, dados):
    """
    Ensures that the demand is only satisfied forward along the route (no backward flow between ports).
    """
    FE = vars["FE"]
    FF = vars["FF"]

    for p in dados.P:
        for j in dados.P:
            if j < p:
                for k in dados.K:
                    for t in dados.T:
                        model.addConstr(
                            FE[p, j, k, t] == 0,
                            name=f"forward_flow_empty_{p}_{j}_{k}_{t}"
                        )
                        for c in dados.C:
                            model.addConstr(
                                FF[p, j, k, c, t] == 0,
                                name=f"forward_flow_full_{p}_{j}_{k}_{c}_{t}"
                            )
    print("Forward flow constraints added.")

def enforce_relation_between_FF_FE_and_ports(model, vars, dados):
    """
    Ensures the relation between FF and FF_port, and between FE and FE_port.
    Aggregates flows by port IDs.
    """
    from gurobipy import quicksum

    FF = vars["FF"]
    FE = vars["FE"]
    FF_port = vars["FF_port"]
    FE_port = vars["FE_port"]

    for k in dados.K:
        for c in dados.C:
            for t in dados.T:
                for i_ in dados.port_nums:
                    for j_ in dados.port_nums:
                        model.addConstr(
                            FF_port[i_, j_, k, c, t] == quicksum([
                                FF[i, j, k, c, t] 
                                for i in dados.P 
                                for j in dados.P 
                                if dados.ordem.loc[i].values[0] == i_ and dados.ordem.loc[j].values[0] == j_
                            ]),
                            name=f'total_FF_by_port_ID_{i_}_{j_}_{k}_{c}_{t}'
                        )

    for k in dados.K:
        for t in dados.T:
            for i_ in dados.port_nums:
                for j_ in dados.port_nums:
                    model.addConstr(
                        FE_port[i_, j_, k, t] == quicksum([
                            FE[i, j, k, t]
                            for i in dados.P
                            for j in dados.P
                            if dados.ordem.loc[i].values[0] == i_ and dados.ordem.loc[j].values[0] == j_
                        ]),
                        name=f'total_FE_by_port_ID_{i_}_{j_}_{k}_{t}'
                    )
    print("Relation between FF and FF_port, and FE and FE_port enforced.")

def enforce_carrier_participation_limits(model, vars, dados):
    """
    Enforces minimum and maximum participation of the carrier in cargo type.
    """
    import math

    FF_port = vars["FF_port"]

    for p in dados.port_nums:
        for j in dados.port_nums:
            for k in dados.K:
                for c in dados.C:
                    for t in dados.T:

                        df_filtered = dados.DF[p, j, k, c, t]
                        px_filtered = dados.PX[(dados.PX['I'] == p) & (dados.PX['C'] == c) & (dados.PX['T'] == t)]
                        pi_filtered = dados.PI[(dados.PI['I'] == p) & (dados.PI['C'] == c) & (dados.PI['T'] == t)]

                        df_value = df_filtered
                        px_value = px_filtered['PX'].values[0]
                        pi_value = pi_filtered['PI'].values[0]

                        model.addConstr(
                            FF_port[p, j, k, c, t] <= math.floor(df_value * px_value),
                            name=f"max_carrier_participation_{p}_{j}_{k}_{c}_{t}"
                        )

                        model.addConstr(
                            FF_port[p, j, k, c, t] >= math.floor(df_value * pi_value),
                            name=f"min_carrier_participation_{p}_{j}_{k}_{c}_{t}"
                        )
    print("Carrier participation limits enforced.")

def enforce_precedence_matrix(model, vars, dados):
    """
    Enforces that the flow respects the precedence matrix between ports.
    """
    FE = vars["FE"]
    FF = vars["FF"]

    for i in dados.P:
        for j in dados.P:
            m = sum(dados.M.loc[p_, i, j].values[0] for p_ in dados.P[i:])
            if m == 0:
                for k in dados.K:
                    for t in dados.T:
                        model.addConstr(
                            FE[i, j, k, t] == 0,
                            name=f"respect_precedence_FE_{i}_{j}_{k}_{t}"
                        )
                        for c in dados.C:
                            model.addConstr(
                                FF[i, j, k, c, t] == 0,
                                name=f"respect_precedence_FF_{i}_{j}_{k}_{c}_{t}"
                            )
    print("Precedence matrix constraints enforced.")

def enforce_empty_container_balance(model, vars, dados):
    """
    Enforces the balance of empty containers at ports.
    """
    E = vars["E"]
    RSE = vars["RSE"]
    RSF = vars["RSF"]
    RLE = vars["RLE"]
    RLF = vars["RLF"]

    count_constr = 0
    for j in dados.port_nums:
        for k in dados.K:
            for t in dados.T:
                count_constr += 1
                model.addConstr(
                    E[j, k, t] == E[j, k, dados.T[-1] if t == 1 else t - 1] + RSE[j, k, t] + RSF[j, k, t] - RLE[j, k, t] - RLF[j, k, t],
                    name=f"empty_container_balance_{j}_{k}_{t}"
                )
    print(f"Empty container balance constraints added: {count_constr}")

def enforce_returned_containers_quantity(model, vars, dados):
    """
    Enforces the quantity of returned containers (RSF, RSE, RLF, RLE) at each port.
    """
    FF_port = vars["FF_port"]
    FE_port = vars["FE_port"]
    RSF = vars["RSF"]
    RSE = vars["RSE"]
    RLF = vars["RLF"]
    RLE = vars["RLE"]

    count_constr = 0
    for j in dados.port_nums:
        for k in dados.K:
            for t in dados.T:
                model.addConstr(
                    RSF[j, k, t] == quicksum(
                        dados.TR(t_, delta, t) * FF_port[i, j, k, c, t_] * dados.SF[(dados.SF['I'] == j) & (dados.SF['K'] == k) & (dados.SF['DT'] == delta)]['SF'].values[0]
                        for i in dados.port_nums
                        for c in dados.C_not_feeder
                        for delta in dados.DT
                        for t_ in dados.T
                    ),
                    name=f"returned_full_containers_{j}_{k}_{t}"
                )

                model.addConstr(
                    RSE[j, k, t] == quicksum(
                        dados.TR(t_, delta, t) * FE_port[i, j, k, t_] * dados.SE[(dados.SE['K'] == k) & (dados.SE['DT'] == delta)]['SE'].values[0]
                        for i in dados.port_nums
                        for delta in dados.DT
                        for t_ in dados.T
                    ),
                    name=f"returned_empty_containers_{j}_{k}_{t}"
                )

                model.addConstr(
                    RLF[j, k, t] == quicksum(
                        dados.TR(t_, delta, t) * dados.LF[(j, k, delta)] * FF_port[i_, j_, k, c, t_]
                        for i_ in dados.port_nums if i_ == j
                        for j_ in dados.port_nums
                        for c in dados.C_not_feeder
                        for delta in dados.DT
                        for t_ in dados.T
                    ),
                    name=f"released_full_containers_{j}_{k}_{t}"
                )

                model.addConstr(
                    RLE[j, k, t] == quicksum(
                        dados.TR(t_, delta, t) * dados.LE[(j, k, delta)] * FE_port[i_, j_, k, t_]
                        for i_ in dados.port_nums if i_ == j
                        for j_ in dados.port_nums
                        for delta in dados.DT
                        for t_ in dados.T
                    ),
                    name=f"released_empty_containers_{j}_{k}_{t}"
                )

                count_constr += 1

    print(f"Returned containers quantity constraints added: {count_constr}")

def enforce_max_empty_containers_per_port(model, vars, dados):
    """
    Enforces the maximum number of empty containers that can be stored at each port.
    """
    E = vars["E"]

    count_constr = 0
    for j in dados.port_nums:
        for t in dados.T:
            model.addConstr(
                quicksum(E[(j, k, t)] * dados.Q[(dados.Q['K'] == k)]['Q'].values[0] for k in dados.K) <= dados.NE[(dados.NE['I'] == j)]['NE'].values[0],
                name=f"max_empty_containers_stored_{j}_{t}"
            )
            for k in dados.K:
                model.addConstr(
                    E[j, k, t] >= 0,
                    name=f"non_negative_empty_containers_{j}_{k}_{t}"
                )
                count_constr += 1

    print(f"Max empty containers per port constraints added: {count_constr}")

def enforce_R_relationship(model, vars, dados):
    """
    Enforces the relationship between R and FF, FE variables.
    """
    R = vars["R"]
    FF = vars["FF"]
    FE = vars["FE"]

    count_constr = 0
    for p in dados.P:
        for t in dados.T:
            model.addConstr(
                R[p, t] == quicksum(    
                    dados.M.loc[p, i, j].values[0]
                    * dados.Q[(dados.Q['K'] == k)]['Q'].values[0] 
                    * FF[i, j, k, c, t]
                    for i in dados.P
                    for j in dados.P
                    for k in dados.K
                    for c in dados.C
                ) + quicksum(
                    dados.M.loc[p, i, j].values[0]
                    * dados.Q[(dados.Q['K'] == k)]['Q'].values[0] 
                    * FE[i, j, k, t]
                    for i in dados.P
                    for j in dados.P
                    for k in dados.K
                ),
                name=f"relationship_R_{p}_{t}"
            )
            count_constr += 1

    print(f"R-FF-FE relationship constraints added: {count_constr}")

def enforce_limit_Rp_t_to_N(model, vars, dados):
    """
    Adds the constraint (5.16) to limit R[p,t] to N.
    """
    R = vars["R"]
    count_constr = 0
    for p in dados.P:
        for t in dados.T:
            model.addConstr(
                R[p, t] <= dados.N,
                name=f"limit_R_{p}_{t}"
            )
            count_constr += 1

    print(f"Constraints added: {count_constr}")

def enforce_deadweight_limit_in_ports(model, vars, dados):
    """
    Adds the constraint for the maximum deadweight in ports, based on the deadweight function.
    """
    FF = vars["FF"]
    FE = vars["FE"]
    count_constr = 0
    index = -1
    for p in dados.P:
        index += 1
        p_ = dados.P[index - 1]
        h = dados.H[dados.H['P'] == p]['H'].values[0]
        h_ = dados.H[dados.H['P'] == p_]['H'].values[0]
        h_value = min(h, h_)
        for t in dados.T:
            count_constr += 1
            # Limite de Deadweight no navio
            model.addConstr(
                quicksum(
                    dados.M.loc[p, i, j].values[0]
                    * dados.WF[(dados.WF['K'] == k) & (dados.WF['C'] == c)]['WF'].values[0] 
                    * FF[i, j, k, c, t]
                    for i in dados.P
                    for j in dados.P
                    for k in dados.K
                    for c in dados.C
                )
                +
                quicksum(
                    dados.M.loc[p, i, j].values[0]
                    * dados.WE[(dados.WE['K'] == k)]['WE'].values[0] 
                    * FE[i, j, k, t]
                    for i in dados.P
                    for j in dados.P
                    for k in dados.K
                )
                <=
                dados.ND * dados.NV / dados.TC,
                name=f"deadweight_max_navio_{p}_{t}"
            )
            
    print(f"Deadweight limit constraints added: {count_constr}")

def enforce_max_refrigerated_containers_on_ships(model, vars, dados):
    """
    Adds the constraint for the maximum number of refrigerated containers on the ships.
    """
    FF = vars["FF"]
    count_constr = 0
    for p in dados.P:
        for t in dados.T:
            count_constr += 1
            model.addConstr(
                quicksum(
                    dados.M.loc[p, i, j].values[0]
                    * FF[i, j, k, c, t]
                    for i in dados.P 
                    for j in dados.P 
                    for k in dados.K_Refrigerados 
                    for c in dados.C
                ) <= dados.NP * dados.NV / dados.TC,
                name=f"max_refrigerated_capacity_{p}_{t}"
            )
    
    print(f"Refrigerated container capacity constraints added: {count_constr}")

def enforce_max_40ft_containers_on_ships(model, vars, dados):
    """
    Adds the constraint for the maximum number of 40-foot containers on the ships.
    """
    FF = vars["FF"]
    FE = vars["FE"]
    count_constr = 0
    for p in dados.P:
        for t in dados.T:
            count_constr += 1
            model.addConstr(
                quicksum(
                    dados.M.loc[p, i, j].values[0]
                    * FF[i, j, k, c, t]
                    for i in dados.P
                    for j in dados.P
                    for k in dados.K_40pes
                    for c in dados.C
                ) + quicksum(
                    dados.M.loc[p, i, j].values[0]
                    * FE[i, j, k, t]
                    for i in dados.P
                    for j in dados.P
                    for k in dados.K_40pes
                ) <= (dados.NV * dados.NF / dados.TC),
                name=f"max_40ft_capacity_{p}_{t}"
            )
    
    print(f"40ft container capacity constraints added: {count_constr}")

def enforce_fleet_capacity_limit(model, vars, dados):
    """
    Adds a constraint to limit the fleet capacity used vs the maximum allowed for each type of cargo.
    """
    FF = vars["FF"]
    FE = vars["FE"]
    E = vars["E"]
    FF_port = vars["FF_port"]
    FE_port = vars["FE_port"]
    
    count_constr = 0
    for k in dados.K:
        for t in dados.T:
            part1 = quicksum(FF[i, j, k, c, t] for i in dados.P for j in dados.P for c in dados.C_not_feeder)
            part2 = quicksum(FE[i, j, k, t] for i in dados.P for j in dados.P)
            part3 = quicksum(E[j, k, t] for j in dados.port_nums)
            
            part4 = quicksum(
                dados.TR(t_, delta, t) * FF[i, j, k, c, t_] * dados.SF[(dados.SF['I'] == dados.ordem.loc[j].values[0]) & (dados.SF['K'] == k) & (dados.SF['DT'] == delta)]['SF'].values[0] +
                dados.TR(t_, delta, t) * FE[i, j, k, t_] * dados.SE[(dados.SE['K'] == k) & (dados.SE['DT'] == delta)]['SE'].values[0]
                for i in dados.P 
                for j in dados.P 
                for c in dados.C_not_feeder
                for delta in dados.DT 
                for t_ in dados.T
                if delta > 1 and dados.TR(t_, delta, t) == 1
            )

            part5 = quicksum(
                dados.TR(t_, delta, t) * dados.LF[j1, k, delta] * FF_port[i, j, k, c, t_] +
                dados.TR(t_, delta, t) * dados.LE[j1, k, delta] * FE_port[i, j, k, t_]
                for i in dados.port_nums
                for j in dados.port_nums 
                for j1 in dados.port_nums
                for c in dados.C_not_feeder
                for delta in dados.DT 
                for t_ in dados.T
                if delta > 1 and dados.TR(t_, delta, t) == 1 and j1 == i
            )
            
            total_sum = part1 + part2 + part3 + part4 + part5
            
            model.addConstr(total_sum <= dados.NC[dados.NC['K'] == k]['NC'].values[0], 
                             name=f"fleet_capacity_limit_{k}_{t}")
            count_constr += 1
    
    print(f"Fleet capacity limit constraints added: {count_constr}")