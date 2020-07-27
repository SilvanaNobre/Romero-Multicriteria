# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 20:33:27 2018

@author: SilvanaNobre
"""

from PyQt5 import QtGui
from operator         import itemgetter, attrgetter, methodcaller
from Plt2_Lib         import *
from Plt2_ResultsForm import *
from Plt2_MtxGen      import *
from Plt2_Results     import *
from Plt2_POffMatrix  import *
from Plt2_MonteCarlo  import *

import sqlite3
import os
import xml.etree.ElementTree
import cfg

import pandas 
import numpy as np

import plotly
import plotly.plotly as py
import plotly.offline as offline
import plotly.graph_objs as go
from plotly.offline import plot

#------------------------------------------------------------------------------
#-(1)------------------------------------------------------- Prepare Parameters
#all parms: global var, optimization, database, montecarlo, prescription writer
#also shows all database parameters
#------------------------------------------------------------------------------

#---------------------------------------------------initialize global variables
#---------------------------------------------------------read from an xml file
GetGlobalVariables('Plt2_GlobalVar.xml')
#--------------------------------------------initialize optimization parameters  
#---------------------------------------------------------read from an xml file
GetOptVariables('Plt2_OptVar.xml')
#-------------------------------------------Set up pre-programmed criteria list
InitObjectiveDic()
InitCriteriaDic()
InitCrtSelectionL()
#------------------------------------------------------------------------------
#------------------------------ conn is defined as a connection to the database  
#--------------------------------------------------to be used in main procedure
#---------------------------------------------------open connection to database
conn = sqlite3.connect(cfg.gvDic['DatabaseFile'])

#-------------------------------- get the last Simulation id saved in the database
with conn: 
    IdSimCursor = conn.cursor()
    str_sql = "SELECT seq FROM SQLITE_SEQUENCE where name = 'Simulation'"
    IdSimCursor.execute(str_sql)
    IdSimList = IdSimCursor.fetchone()
    cfg.gvDic['idSimulation'] = IdSimList[0] 
    IdSimCursor.close()
    
#-------------------------------- get the last Simulation name in the database
with conn: 
    SimNameCursor = conn.cursor()
    str_sql = "SELECT SimName FROM Simulation where idSimulation = " + str(cfg.gvDic['idSimulation'])
    SimNameCursor.execute(str_sql)
    SimNameList = SimNameCursor.fetchone()
    cfg.gvDic['SimName'] = SimNameList[0] 
    SimNameCursor.close()    
    
#------------------------------------ get the last Result saved in the database
with conn: 
    IdResultCursor = conn.cursor()
    str_sql = "SELECT seq FROM SQLITE_SEQUENCE where name = 'Results'"
    IdResultCursor.execute(str_sql)
    IdResultList = IdResultCursor.fetchone()
    cfg.LastIdResult = IdResultList[0] 
    cfg.BeforeMatrixIdResult = IdResultList[0]    
    IdResultCursor.close()

# ----------------------------------------------create an app for Qt windows 
MyApp = QApplication(sys.argv)


#------------------------------------create the Connection to database    
dbResults = QtSql.QSqlDatabase()
dbResults = QtSql.QSqlDatabase.addDatabase('QSQLITE')
dbResults.setDatabaseName(cfg.gvDic['DatabaseFile'])
if dbResults.isValid(): print("SQL db instance OK")
else: 
   print("SQL db instance error = "+ dbResults.lastError().text())
     
if dbResults.open(): print("Database connected")  
else: print(dbResults.lastError().text())

# ----------------------------------------------Call Select simulation window 
SelectSimulaton('Plt2_SelectSimulation.ui', MyApp)
MyApp.quit()  
dbResults.close() 

#-----------------------------------------------Selected criteria
# a partir dos objetivos dessa simulação, colocar na tela os objetivos para o usuário quais quer fazer pareto
# depois da tela
# alimentar as variáveis cfg.CrtParetoDic e cfg.CrtOrderDic[4]
# daqui prá frente consideramos que essas variáveis já estão prontas
# fazer a tela
VarInList = ""

for item in cfg.CrtParetoDic.keys():
    if VarInList != "" :
       VarInList = VarInList + "," 
    VarInList = VarInList + "'" + item +  "'"
print(VarInList)

#------------------------------------ save Simulation inPareto Table 
with conn: 
    ParetoDel = conn.cursor()
    str_sql = "Delete from ResPareto where idSimulation = " + str(cfg.gvDic['idSimulation'])
    ParetoDel.execute(str_sql)
    ParetoDel.close()    

    ParetoIns = conn.cursor()
    str_sql = "Insert into ResPareto (idResult, idSimulation, Iteration, PlotPoint, Variable, Objective, Value) "\
            + "select r.idResult, r.idSimulation, r.mcIteration, r.PlotPoint, v.Variable, r.Objective, v.Value "\
            + "  from Results r inner join ResVariable v on v.idResult = r.idResult "\
            + " where r.idSimulation = "+ str(cfg.gvDic['idSimulation']) +" and r.RunType = 'Pareto' "\
            + "   and v.Variable in ("+VarInList+") "\
            + " order by r.idResult,  v.Variable "         
    ParetoIns.execute(str_sql)
    ParetoIns.close()   

# isso ainda nao está pronto, é só um exemplo de gráfico
    
SqlGraph = " select r1.PlotPoint, r1.Value xTotalProd, r3.Value xTotalNPV, r4.Value xTotalMktDev "\
         + "   from            ResPareto r1 "\
         + "        inner join ResPareto r3 on (r3.Variable = 'xTotalNPV'  and  r3.idSimulation = r1.idSimulation and r3.idResult = r1.idResult) "\
         + "        inner join ResPareto r4 on (r4.Variable = 'xTotalMktDev' and  r4.idSimulation = r1.idSimulation and r4.idResult = r1.idResult) "\
         + "  where r1.idSimulation = "+ str(cfg.gvDic['idSimulation']) +"   and r1.Variable = 'xTotalProd' "\

         
dfGraph = pandas.read_sql_query(SqlGraph, conn)
graphTitle = 'Pareto Frontier'

fig = {'data' : [{'x':    dfGraph['xTotalIgor'], 
                  'y':    dfGraph['xTotalNPV'],
                  'z':    dfGraph['xTotalProd'],
                  'mode': 'lines'
                 } 
                ], 
    
       'layout': {'xaxis': {'title': 'TotalIgor'},
                  'yaxis': {'title': 'TotalNPV'},
                  'zaxis': {'title': 'TotalProd'},
                  'title': graphTitle
                  } 
       }

offline.plot(fig)    
            
                

conn.close() 


#end Plt2_ParetoMain      
