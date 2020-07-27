# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 12:16:32 2018

@author: SilvanaNobre
"""

global DicTable
global DicJoin

DicTable = {}
DicJoin  = {}

#        TableName      =   Fileds Names,    Integer Columns, Float Columns
DicTable['Variable']    = [['Variable','DscVariable','FlagCriteria'],[],[]]
DicTable['Region']      = [['idRegion','Name'],[],[]]
DicTable['Market']      = [['idMarket','Name','addCost'],[],[2]]
DicTable['Species']     = [['idSpecies','Description','pcOcupationMin','pcOcupationMax','pcGoal','CarbonFactor'],[],[2,3,4,5]]
DicTable['Product']     = [['idProducts','Description'],[],[]] 
DicTable['InitialArea'] = [['idMgmtUnit','Description','idRegion','idSpecies','Cycle','Rotation','Age','Area','LEV'],[4,5,6,7],[8]]
DicTable['Production']  = [['idProduction','ttype','idRegion','idSpecies','idProduct','CutAge','Production'] ,[5],[6]]
DicTable['MarketDemand']= [['idMktDemand','idPeriod','idMarket','idSpecies','idProduct','Volume','VolumeMin'],[1,5,6],[]]  
DicTable['Price']       = [['idPrice','idPeriod','idMarket','idSpecies','idProduct','Price'],[1],[5]]
DicTable['Period']      = [['idPeriod','CrbSeq','CrbPrice'],[0],[1,2]]
DicTable['HarvCosts']   = [['idHarvCosts','ttype','idSpecies','idProduct','Cost'],[],[4]]
DicTable['SilvCosts']   = [['idSilvCost','ttype','idRegion','idSpecies','Age','Cost'],[4],[5]]

DicJoin['Variable']    =  [(2,('FlagCriteria', 'FlagCriteria', 'Description'))]
DicJoin['Region']      =  []
DicJoin['Market']      =  []
DicJoin['Species']     =  []
DicJoin['Product']     =  []
DicJoin['InitialArea'] =  [(2,('Region', 'idRegion', 'Name')), 
                           (3,('Species', 'idspecies', 'Description'))]
DicJoin['Production']  =  [(2,('Region', 'idRegion', 'Name')), 
                           (3,('Species', 'idspecies', 'Description')), 
                           (4,('Product', 'idProduct', 'Description'))]
DicJoin['MarketDemand']=  [(2,('Market', 'idMarket', 'Name')), 
                           (3,('Species', 'idspecies', 'Description')), 
                           (4,('Product', 'idProduct', 'Description'))]
DicJoin['Price']       =  [(2,('Market', 'idMarket', 'Name')), 
                           (3,('Species', 'idspecies', 'Description')), 
                           (4,('Product', 'idProduct', 'Description'))]
DicJoin['Period']      =  [] 
DicJoin['HarvCosts']   =  [(2,('Species', 'idspecies', 'Description')), 
                           (3,('Product', 'idProduct', 'Description'))]
DicJoin['SilvCosts']   = [(2,('Region', 'idRegion', 'Name')), 
                          (3,('Species', 'idspecies', 'Description'))]