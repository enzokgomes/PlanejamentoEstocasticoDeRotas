# -*- coding: utf-8 -*-
"""
Created on Sun May  12 22:49:20 2024

@author: lucas
"""

#---------------------------------------------------------------------------------------------------------------------------------------#
import pandas as pd
import itertools
import Services.matriz_precedencia as mp
#---------------------------------------------------------------------------------------------------------------------------------------#
def rotate(l, n):
            return l[n:] + l[:n]

class Dados:

    def __init__(self, file_name):
        

        # Connection with the spreadsheet
        xls = pd.ExcelFile(file_name)

        self.Rota = pd.read_excel(xls, 'ROTA', usecols='A:B')

        self.De_Para_Portos = pd.read_excel(xls, 'DE-PARA', usecols='A:B')

        self.De_Para_Trechos = pd.read_excel(xls, 'DE-PARA', usecols='D:E')

        self.De_Para_K = pd.read_excel(xls, 'DE-PARA', usecols='G:H')

        self.De_Para_C = pd.read_excel(xls, 'DE-PARA', usecols='J:K')

        self.De_Para_T = pd.read_excel(xls, 'DE-PARA', usecols='M:N')

        # Separa os dados em NB e SB
        self.NB = self.Rota[self.Rota["Porto"].str.startswith("NB")]["IdPorto"].tolist()
        self.SB = self.Rota[self.Rota["Porto"].str.startswith("SB")]["IdPorto"].tolist()

        # Obtém a matriz de precedência a partir da rota
        self.M = mp.gerar_matriz_precedencia(self.NB, self.SB)

        # Ordem dos portos
        ordem = self.NB + self.SB

        # Indexação dos portos
        self.ordem = pd.DataFrame(0, index=[i + 1 for i in range(len(ordem))], columns=['IdPorto', 'DP', 'TO'])

        for i in range(len(ordem)):
            self.ordem.loc[i + 1, 'IdPorto'] = ordem[i]

        self.port_nums = self.ordem['IdPorto'].drop_duplicates().values
        self.port_nums.sort()

        # Definir conjuntos (como exemplo, defina os conjuntos de portos, tipos de contêineres, etc.)
        self.P = range(1, len(ordem) + 1) 
        self.K = range(1, 5)   # Exemplo de 4 tipos de contêineres
        self.K_Refrigerados = [2,4]
        self.K_Nao_Refrigerados = [1,3]
        self.K_40pes = [1, 2]
        self.C = range(1, 3)   # Exemplo de 2 tipos de carga
        self.T = range(1, 13)  # Exemplo de 12 períodos de tempo
        self.DT = range(0, 4)  # Exemplo com deltas de 0 a 3

        # DP - Distância entre os portos
        self.DP = pd.read_excel(xls, 'PAR DP', usecols='A:C')

        for i in self.P[:-1]:
            saida = self.ordem.loc[i].values[0]
            chegada = self.ordem.loc[i+1].values[0]
            self.ordem.loc[i, 'DP'] = self.DP[(self.DP['I'] == saida) & (self.DP['J'] == chegada)]['DP'].values[0]

        # DF - Demanda
        self.DF = pd.read_excel(xls, 'PAR DF', usecols='R:W')
        all_combinations = list(itertools.product(self.port_nums, self.port_nums, self.K, self.C, self.T))
        df = pd.DataFrame()
        df[['Key']] = self.DF[['I','J','K','C','T']].apply(tuple, axis=1).to_frame()
        df[['Values']] = self.DF[['DF']]
        result_dict = dict(zip(df['Key'], df['Values']))
        # Fill missing combinations with zeros
        for combination in all_combinations:
            if combination not in result_dict:
                result_dict[combination] = 0
        self.DF = result_dict

        # CF - Custo de mover contêiner cheio
        self.CF = pd.read_excel(xls, 'PAR CF', usecols='H:K')

        # CE - Custo de mover contêiner vazio
        self.CE = pd.read_excel(xls, 'PAR CE', usecols='H:K')

        # CS - Custo de estoque
        self.CS = pd.read_excel(xls, 'PAR CS', usecols='D:E')

        # CSC - Custo de escala (falta implementar)
        self.CSC = pd.read_excel(xls, 'PAR CSC', usecols='A:C')

        # CR - Custo de reparo
        self.CR = pd.read_excel(xls, 'PAR CR', usecols='G:I')

        # CM - Custo do tipo de carga
        self.CM = pd.read_excel(xls, 'PAR CM', usecols='D:E')

        # RF - Receita
        self.RF = pd.read_excel(xls, 'PAR RF', usecols='R:W')

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
        self.H = pd.read_excel(xls, 'PAR H', usecols='E:G')
        # O que é NB vs SB?

        # NV - Número de navios alocados na rota 
        self.NV = pd.read_excel(xls, 'PAR NV', usecols='B').columns[0]
        
        # VC - Viagem redonda?
        self.TC = pd.read_excel(xls, 'PAR VC', usecols='B').columns[0]
        # O que significa 0,93 no parâmetro de viagem redonda? Achei que seria bool (0 ou 1)
        
        # NT - Capacidade do navio em TEUs
        self.NT = pd.read_excel(xls, 'PAR NT', usecols='B').columns[0]
        
        # ND - Deadweight de carga
        self.ND = pd.read_excel(xls, 'PAR ND', usecols='B').columns[0]
        
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

        self.LF = {}
        self.LE = {}

        for j in self.port_nums:
            for k in self.K:
                for delta in self.DT:
                    # Create a variable with the current index (J, K, Delta)
                    self.LF[(j, k, delta)] = 1 if delta == 0 else 0
                    self.LE[(j, k, delta)] = 1 if delta == 0 else 0
        
        xls.close()