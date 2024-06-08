# -*- coding: utf-8 -*-
"""
Created on Sun May  12 22:49:20 2024

@author: lucas
"""

#---------------------------------------------------------------------------------------------------------------------------------------#
import pandas as pd
#---------------------------------------------------------------------------------------------------------------------------------------#
class Dados:

    def __init__(self, file_name):

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
        self.VV = pd.read_excel(xls, 'PAR VV', usecols='B').columns[0]
        
        # VC - Viagem redonda?
        self.VC = pd.read_excel(xls, 'PAR VC', usecols='B').columns[0]
        # O que significa 0,93 no parâmetro de viagem redonda? Achei que seria bool (0 ou 1)
        
        # VT - Capacidade do navio em TEUs
        self.VT = pd.read_excel(xls, 'PAR VT', usecols='B').columns[0]
        
        # VD - Deadweight de carga
        self.VD = pd.read_excel(xls, 'PAR VD', usecols='B').columns[0]
        
        # NP - Capacidade máxima de plugs para contêineres refrigerados
        self.NP = pd.read_excel(xls, 'PAR NP', usecols='B').columns[0]

        # NF - Capacidade maxima de contêineres de 40 pés
        self.NF = pd.read_excel(xls, 'PAR NF', usecols='B').columns[0]

        # NE - Capacidade máxima de estoque
        self.NE = pd.read_excel(xls, 'PAR NE', usecols='D:E')

        # Read NC
        self.NC = pd.read_excel(xls, 'PAR NC', usecols='D:E')

        # G - 0 (dry) / 1 (reefer)
        self.G = pd.read_excel(xls, 'PAR G', usecols='A:B', nrows=4)

        # Read Q
        self.Q = pd.read_excel(xls, 'PAR Q', usecols='A:B', nrows=4)
        
        # Par N
        self.N = self.VV * self.VT / self.VC
        