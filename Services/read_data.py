#---------------------------------------------------------------------------------------------------------------------------------------#
import pandas as pd
import itertools
import Services.matriz_precedencia as mp
from openpyxl import load_workbook
import math
#---------------------------------------------------------------------------------------------------------------------------------------#
def rotate(l, n):
            return l[n:] + l[:n]

class Dados:

    def __init__(self, file_name):
        

        # Connection with the spreadsheet
        xls = pd.ExcelFile(file_name)

        # Obtém a rota
        self.Rota = pd.read_excel(xls, 'ROTA', usecols='A:B')

        # Obtém a tabela 'DE-PARA' para os portos
        self.De_Para_Portos = pd.read_excel(xls, 'DE-PARA', usecols='A:B')

        # Confere se MAO está na rota
        self.MAO_index = None
        adj_index = [string[-3:] for string in self.Rota['Porto']]
        self.is_MAO = 'MAO' in adj_index
        if self.is_MAO:
            self.MAO_index = self.Rota.iloc[adj_index.index('MAO'), 1]
            # PAR MAO-VLC (custo balsa Manaus-Belém e margem)
            self.MAO_VLC = pd.read_excel(xls, 'PAR MAO-VLC', usecols='A:C', index_col=0)
            self.custo_balsa_mao_vlc = self.MAO_VLC.loc['Custo Balsa', 'Valor'] / (1 - self.MAO_VLC.loc['Margem de Lucro', 'Valor'])
            self.VLC_index = self.De_Para_Portos[self.De_Para_Portos['De'] == 'VLC']['Para'].values[0]
            print(f"VLC Index: {self.VLC_index}")
        print(f'MAO Index: {self.MAO_index}')

        # Obtém a tabela 'DE-PARA' para os trechos
        self.De_Para_Trechos = pd.read_excel(xls, 'DE-PARA', usecols='D:E')

        # Obtém a tabela 'DE-PARA' para os contêineres
        self.De_Para_K = pd.read_excel(xls, 'DE-PARA', usecols='G:H')

        # Obtém a tabela 'DE-PARA' para os tipos de carga
        self.De_Para_C = pd.read_excel(xls, 'DE-PARA', usecols='J:K')

        # Obtém a tabela 'DE-PARA' para os períodos de tempo
        self.De_Para_T = pd.read_excel(xls, 'DE-PARA', usecols='M:N')

        # Separa os dados em NB e SB
        self.NB = self.Rota[self.Rota["Porto"].str.startswith("NB")]["IdPorto"].tolist()
        self.SB = self.Rota[self.Rota["Porto"].str.startswith("SB")]["IdPorto"].tolist()

        # Obtém a matriz de precedência a partir da rota
        self.M = mp.gerar_matriz_precedencia(self.NB, self.SB)

        # Ordem dos portos
        ordem = self.NB + self.SB

        # Indexação dos portos
        self.ordem = pd.DataFrame(0.0, index=[i + 1 for i in range(len(ordem))], columns=['IdPorto', 'DP', 'TO'])

        for i in range(len(ordem)):
            self.ordem.loc[i + 1, 'IdPorto'] = ordem[i]

        self.port_nums = self.ordem['IdPorto'].drop_duplicates().values
        self.port_nums.sort()

        # Definir conjuntos (como exemplo, defina os conjuntos de portos, tipos de contêineres, etc.)
        self.P = range(1, len(ordem) + 1) 
        self.K = range(1, 5)   # 4 tipos de contêineres
        self.K_Refrigerados = [2,4]
        self.K_Nao_Refrigerados = [1,3] 
        self.K_40pes = [1, 2]
        self.C = range(1, 3)   # 2 tipos de carga [1, 2]
        self.C_feeder = [2]
        self.C_not_feeder = [c for c in self.C if c not in self.C_feeder]
        self.T = range(1, 13)  # 12 meses
        self.DT = range(0, 4)  # deltas de 0 a 3

        # DP - Distância entre os portos
        self.DP = pd.read_excel(xls, 'PAR DP', usecols='A:C')

        # DC - Distância entre as cidades
        self.DCID = pd.read_excel(xls, 'PAR DCID', usecols='A:C')

        for i in self.P[:-1]:
            saida = self.ordem.loc[i].values[0]
            chegada = self.ordem.loc[i+1].values[0]
            if saida == chegada:
                self.ordem.loc[i, 'DP'] = 0
                continue
            if saida == self.MAO_index:
                saida = self.VLC_index
            if chegada == self.MAO_index:
                chegada = self.VLC_index
            self.ordem.loc[i, 'DP'] = self.DP[(self.DP['I'] == saida) & (self.DP['J'] == chegada)]['DP'].values[0]

        # FEEDER - % de carga feeder por origem e destino
        # FEEDER é o C tipo 2
        self.FEEDER = pd.read_excel(xls, 'PAR FEEDER', usecols='A:C')

        # DF - Demanda
        self.DF = pd.read_excel(xls, 'PAR DF', usecols='R:V')

        df_expanded = pd.DataFrame(columns=['I', 'J', 'K', 'C', 'T', 'DF'])
        for index, row in self.DF.iterrows():
            i = row['I']
            j = row['J']
            k = row['K']
            t = row['T']
            demanda_total = row['DF']
            percent_feeder = self.FEEDER[(self.FEEDER['I'] == i) & (self.FEEDER['J'] == j)]['PERCENT_FEEDER'].values
            if len(percent_feeder) > 0:
                percent_feeder = percent_feeder[0]
            else:
                percent_feeder = 0
            demanda_feeder = round(demanda_total * percent_feeder)
            demanda_not_feeder = round(demanda_total * (1 - percent_feeder))
            df_expanded = pd.concat([df_expanded, pd.DataFrame({'I': [i], 'J': [j], 'K': [k], 'C': [2], 'T': [t], 'DF': [demanda_feeder]})], ignore_index=True)
            df_expanded = pd.concat([df_expanded, pd.DataFrame({'I': [i], 'J': [j], 'K': [k], 'C': [1], 'T': [t], 'DF': [demanda_not_feeder]})], ignore_index=True)
        self.DF = df_expanded

        all_combinations = list(itertools.product(self.port_nums, self.port_nums, self.K, self.C, self.T))
        df = pd.DataFrame()
        df[['Key']] = self.DF[['I','J','K','C','T']].apply(tuple, axis=1).to_frame()
        df[['Values']] = self.DF[['DF']]
        result_dict = dict(zip(df['Key'], df['Values']))
        
        # Completa os valores restantes com 0
        for combination in all_combinations:
            if combination not in result_dict:
                result_dict[combination] = 0
        self.DF = result_dict
        
        # Botar na Planilha
        self.demanda_total = 842115 # XXXXXXXXXXXXXXXX

        # CF - Custo de mover contêiner cheio
        self.CF = pd.read_excel(xls, 'PAR CF', usecols='H:K')

        # CE - Custo de mover contêiner vazio
        self.CE = pd.read_excel(xls, 'PAR CE', usecols='H:K')

        # CS - Custo de estoque
        self.CS = pd.read_excel(xls, 'PAR CS', usecols='D:E')

        # CSC - Custo de escala
        self.CSC = pd.read_excel(xls, 'PAR CSC', usecols='A:C')

        # CR - Custo de reparo
        self.CR = pd.read_excel(xls, 'PAR CR', usecols='G:I')

        # CM - Custo do tipo de carga
        self.CM = pd.read_excel(xls, 'PAR CM', usecols='D:E')

        # CV - Custo de afretamento por navio
        self.CV = pd.read_excel(xls, 'PAR CV', usecols='A:B')

        # CI - Dados do Frete / Custo Intermodal (nova estrutura: PARAMETER, DRY, REFFER, UNIT)
        self.CI = pd.read_excel(xls, 'PAR INTERMODAL', usecols='A:D')
        # Índice por nome do parâmetro; normalizar margem para decimal
        first_col = self.CI.columns[0]
        self.CI = self.CI.set_index(first_col)
        self.CI.index = self.CI.index.astype(str).str.strip()


        # E0 - Estoque inicial
        self.E0 = pd.read_excel(xls, 'PAR E0', usecols='G:I')

        # FUEL - Custo de combustível (VLSFO, MDO)
        self.FUEL = pd.read_excel(xls, 'PAR FUEL', usecols='A:C')

        # MC - Taxa de consumo de MDO em viagem e no porto
        self.MC = pd.read_excel(xls, 'PAR MC', usecols='A:B')

        # DC - Distância entre porto e capital
        self.DC = pd.read_excel(xls, 'PAR DEPOTS', usecols='A:B') # Alterar nome da aba para DC

        # WF - Peso do contêiner cheio
        self.WF = pd.read_excel(xls, 'PAR WF', usecols='G:I')
        # Alguns não têm peso?

        # WE - Peso do contêiner vazio
        self.WE = pd.read_excel(xls, 'PAR WE', usecols='D:E')

        # PX - Share máximo de participação no tipo de carga
        self.PX = pd.read_excel(xls, 'PAR PX', usecols='P:S')

        # PI - Share mínimo de participação no tipo de carga
        self.PI = pd.read_excel(xls, 'PAR PI', usecols='P:S')

        # SF - Taxa de retorno dos contêineres
        self.SF = pd.read_excel(xls, 'PAR SF', usecols='H:K')

        # SE - Taxa retorno dos contêineres
        self.SE = pd.read_excel(xls, 'PAR SE', usecols='G:I')

        # TR - Relação entre instantes de tempo
        self.TR = lambda t, delta, t_ : 1 if (t + delta - t_) % len(self.T) == 0 else 0

        # TM - Tempo de movimentação de contêineres (contêineres/h)
        self.TM = pd.read_excel(xls, 'PAR TM', usecols='A:B')

        # TO - Tempo de operação portuária (em horas) - entrada, atracagem, saída
        self.TO = pd.read_excel(xls, 'PAR TO', usecols='A:B')

        for i in self.P:
             porto = self.ordem.loc[i].values[0]
             self.ordem.loc[i, 'TO'] = self.TO[self.TO['I'] == porto]['TO'].values[0]

        # USD - Valor de dólar considerado (para ajustar preço do combustível, assumindo que os outros custos já estão em reais)
        self.USD = pd.read_excel(xls, 'PAR USD', usecols='A:C')

        # H - Deadweight
        self.H = pd.read_excel(xls, 'PAR H', usecols='F:G')

        # NV - Número de navios alocados na rota 
        self.NV = pd.read_excel(xls, 'PAR NV', usecols='B').columns[0]
        
        # VC - Viagem redonda?
        self.TC = pd.read_excel(xls, 'PAR VC', usecols='B').columns[0]
        
        # NT - Capacidade do navio em TEUs
        self.NT = pd.read_excel(xls, 'PAR NT', usecols='B').columns[0]
        
        # ND - Deadweight de carga
        self.ND = pd.read_excel(xls, 'PAR ND', usecols='A:B')
        vessel_nt = self.ND['NT'].iloc[(self.ND['NT'] - self.NT).abs().argsort()[:1]].values[0]
        self.ND = self.ND[self.ND['NT'] == vessel_nt]['ND'].values[0]
        
        # NP - Capacidade máxima de plugs para contêineres refrigerados
        self.NP = pd.read_excel(xls, 'PAR NP', usecols='B').columns[0]

        # NF - Capacidade maxima de contêineres de 40 pés
        self.NF = pd.read_excel(xls, 'PAR NF', usecols='B').columns[0]

        # NE - Capacidade de armazenagem de vazios no porto i
        self.NE = pd.read_excel(xls, 'PAR NE', usecols='D:E')

        # NC - Frota disponível de contêineres de índice k
        self.NC = pd.read_excel(xls, 'PAR NC', usecols='D:E')

        # G - 0 (dry) / 1 (reefer)
        self.G = pd.read_excel(xls, 'PAR G', usecols='A:B', nrows=4)

        # Q - TEUs ocupados por um contêiner de índice k
        self.Q = pd.read_excel(xls, 'PAR Q', usecols='A:B', nrows=4)
        
        # Par N
        self.N = self.NV * self.NT / self.TC

        # Define LF e LE como 1 para delta 0 e 0 para os demais deltas
        self.LF = {}
        self.LE = {}

        for j in self.port_nums:
            for k in self.K:
                for delta in self.DT:
                    # Create a variable with the current index (J, K, Delta)
                    self.LF[(j, k, delta)] = 1 if delta == 0 else 0
                    self.LE[(j, k, delta)] = 1 if delta == 0 else 0

        
        distancia_viagem = self.ordem['DP'].sum()

        # Custo VLSFO geral ou por trecho?   
        vs = 14 * 0.5144 * 3.6
        tempo_viagem = distancia_viagem / vs
        custo_VLSFO = (0.006754*vs**3 +37.23) * tempo_viagem \
            * self.FUEL[self.FUEL['Combustível'] == 'VLSFO']['Preço'].values[0] * self.USD['Valor'].values[0] * self.NV
            
        consumo_MDO_viagem = self.MC[self.MC['MDO Consumption'] == 'Sea']['t/day'].values[0]
        consumo_MDO_porto = self.MC[self.MC['MDO Consumption'] == 'Port']['t/day'].values[0]
        
        consumo_MDO_total = ((28 - tempo_viagem) * consumo_MDO_porto + tempo_viagem * consumo_MDO_viagem) * self.NV

        # Custo Afretamento
        custo_diario_afretamento = self.CV[self.CV['NT'] == vessel_nt]['CV'].values[0] * self.USD['Valor'].values[0] * self.NV
        custo_afretamento = custo_diario_afretamento * 28

        # Custo Escala
        CSC_ports = self.NB[:-1] + self.SB[:-1]
        custo_escala = 0
        for port in CSC_ports:
            custo_escala += self.CSC[(self.CSC['I'] == port) & (self.CSC['NT'] == vessel_nt)]['CSC'].values[0]
        custo_escala *= self.NV

        # Cálculo do Slot Cost
        self.slot_cost = (custo_VLSFO + consumo_MDO_total + custo_afretamento + custo_escala) / (self.NV * self.NT * (1 - 0.15) * (len(ordem) - 2))
        print(f'Slot Cost: {self.slot_cost}')
        # Fecha a conexão com a planilha
        xls.close()

        # RF - Receita (calculada a partir de PAR INTERMODAL e PAR MAO-VLC)
        self._compute_rf()


    def _get_ci_param(self, param_key, cargo_type):
        """Obtém parâmetro do PAR INTERMODAL (param_key pode ser parcial, cargo_type = 'DRY' ou 'REEFER')."""
        col = cargo_type if cargo_type in self.CI.columns else None
        if col is None:
            return None
        for idx in self.CI.index:
            if param_key.lower() in str(idx).lower():
                v = self.CI.loc[idx, col]
                if pd.notna(v):
                    return float(v)
        return None

    def _compute_rf(self):
        """Calcula self.RF a partir do intermodal."""
        # Parâmetros por tipo de carga (nomes flexíveis no Excel)
        def get_coef(ctype):
            v = self._get_ci_param('Cost Coefficient', ctype)
            return float(v) if v is not None else 0.0
        def get_load(ctype):
            v = self._get_ci_param('Load/Discharge', ctype)
            return float(v) if v is not None else 0.0
        def get_margin(ctype):
            v = self._get_ci_param('Margin', ctype)
            if v is None:
                return 0.15
            return float(v) if v <= 1 else v / 100.0


        rows = []
        for i in self.port_nums:
            for j in self.port_nums:
                if i != j:
                    for k in self.K:
                        for t in self.T:
                            for c in self.C_not_feeder:

                                is_reefer = k in self.K_Refrigerados
                                ctype = 'REEFER' if is_reefer else 'DRY'
                                cost_coef = get_coef(ctype)
                                load_discharge = get_load(ctype)
                                margin = get_margin(ctype)
                                denom = 1.0 - margin
                                if denom <= 0:
                                    denom = 1.0

                                if self.is_MAO and i == self.MAO_index:
                                    dist = self.DCID[(self.DCID['I'] == self.VLC_index) & (self.DCID['J'] == j)]['DCID'].values[0]
                                    base_rf = (dist * cost_coef + load_discharge) / denom + self.custo_balsa_mao_vlc

                                elif self.is_MAO and j == self.MAO_index:
                                    dist = self.DCID[(self.DCID['I'] == i) & (self.DCID['J'] == self.VLC_index)]['DCID'].values[0]
                                    base_rf = (dist * cost_coef + load_discharge) / denom + self.custo_balsa_mao_vlc

                                else:
                                    dist = self.DCID[(self.DCID['I'] == i) & (self.DCID['J'] == j)]['DCID'].values[0]
                                    base_rf = (dist * cost_coef + load_discharge) / denom
                                rows.append({'I': i, 'J': j, 'K': k, 'C': c, 'T': t, 'RF': base_rf})

                            for c in self.C_feeder:
                                # Feeder Slot Cost is defined per TEU, double if conteiner is 40 feet (2 TEU)
                                is_40_feet = k in self.K_40pes
                                feeder_cost = self.slot_cost * (1 + is_40_feet)
                                rows.append({'I': i, 'J': j, 'K': k, 'C': c, 'T': t, 'RF': feeder_cost})

        self.RF = pd.DataFrame(rows)

        self.RF.to_excel("RF_Export.xlsx")