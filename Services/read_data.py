# -*- coding: utf-8 -*-
"""
Created on Sun May  12 22:49:20 2024

@author: lucas
"""

#---------------------------------------------------------------------------------------------------------------------------------------#
import pandas as pd
#---------------------------------------------------------------------------------------------------------------------------------------#
def rotate(l, n):
            return l[n:] + l[:n]

class Dados:

    def __init__(self, file_name):
        # Definir conjuntos (como exemplo, defina os conjuntos de portos, tipos de contêineres, etc.)
        self.P = range(1, 11)  # Exemplo de 10 portos
        self.K = range(1, 5)   # Exemplo de 3 tipos de contêineres
        self.C = range(1, 3)   # Exemplo de 5 tipos de carga
        self.T = range(1, 13)  # Exemplo de 12 períodos de tempo

        # Connection with the spreadsheet
        xls = pd.ExcelFile(file_name)

        # DF - Demanda
        self.DF = pd.read_excel(xls, 'PAR DF', usecols='R:W')

        # CF - Custo de mover contêiner cheio
        self.CF = pd.read_excel(xls, 'PAR CF', usecols='H:K')

        # CE - Custo de mover contêiner vazio
        self.CE = pd.read_excel(xls, 'PAR CE', usecols='H:K')

        # CS - Custo de estoque
        self.CS = pd.read_excel(xls, 'PAR CS', usecols='D:E')

        # CR - Custo de reparo
        self.CR = pd.read_excel(xls, 'PAR CR', usecols='G:I')

        # CM - Custo do tipo de carga
        self.CM = pd.read_excel(xls, 'PAR CM', usecols='D:E')

        # RF - Receita
        self.RF = pd.read_excel(xls, 'PAR RF', usecols='R:W')

        # E0 - Estoque inicial
        self.E0 = pd.read_excel(xls, 'PAR E0', usecols='G:I')

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

        # TR - Correlação tempo com a taxa de retorno
        self.TR = pd.read_excel(xls, 'PAR TR', usecols='P:S')

        # H - Deadweight
        self.H = pd.read_excel(xls, 'PAR H', usecols='E:G')
        # O que é NB vs SB?

        # M - Matriz de precedência
        self.M = pd.read_excel(xls, 'PAR M', usecols='J:M')

        # VV - Número de navios alocados na rota 
        self.NV = pd.read_excel(xls, 'PAR VV', usecols='B').columns[0]
        
        # VC - Viagem redonda?
        self.TC = pd.read_excel(xls, 'PAR VC', usecols='B').columns[0]
        # O que significa 0,93 no parâmetro de viagem redonda? Achei que seria bool (0 ou 1)
        
        # VT - Capacidade do navio em TEUs
        self.NT = pd.read_excel(xls, 'PAR VT', usecols='B').columns[0]
        
        # VD - Deadweight de carga
        self.ND = pd.read_excel(xls, 'PAR VD', usecols='B').columns[0]
        
        # NP - Capacidade máxima de plugs para contêineres refrigerados
        self.NP = pd.read_excel(xls, 'PAR NP', usecols='B').columns[0]

        # NF - Capacidade maxima de contêineres de 40 pés
        self.NF = pd.read_excel(xls, 'PAR NF', usecols='B').columns[0]

        # NE - Capacidade de armazenagem de vazios no porto i
        self.NE = pd.read_excel(xls, 'PAR NE', usecols='D:E')

        # Read NC
        self.NC = pd.read_excel(xls, 'PAR NC', usecols='D:E')

        # G - 0 (dry) / 1 (reefer)
        self.G = pd.read_excel(xls, 'PAR G', usecols='A:B', nrows=4)

        # Read Q
        self.Q = pd.read_excel(xls, 'PAR Q', usecols='A:B', nrows=4)
        
        # Par N
        self.N = self.NV * self.NT / self.TC

        self.LF = {}
        self.LE = {}

        for j in self.P:
            for k in self.K:
                for delta in self.T:
                    # Create a variable with the current index (J, K, Delta)
                    self.LF[(j, k, delta)] = 0.8 if delta == 1 else 0.2 if delta == 2 else 0
                    self.LE[(j, k, delta)] = 0.8 if delta == 1 else 0.2 if delta == 2 else 0
        
        self.TR = {}
        T = [i for i in self.T]
        for t in range(len(T)):
            for t_linha in range(len(T)):
                for delta in T:
                    self.TR[T[t], delta, T[t_linha]] = 1 if T[t] == rotate(T, delta)[t_linha] else 0