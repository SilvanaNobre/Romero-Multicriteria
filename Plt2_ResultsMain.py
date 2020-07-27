# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 14:45:16 2018

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

#-------------------------------- get the last Simulation saved in the database
with conn: 
    IdSimCursor = conn.cursor()
    str_sql = "SELECT seq FROM SQLITE_SEQUENCE where name = 'Simulation'"
    IdSimCursor.execute(str_sql)
    IdSimList = IdSimCursor.fetchone()
    cfg.gvDic['idSimulation'] = IdSimList[0] 
    IdSimCursor.close()
    
#-------------------------------- get the last Simulation saved in the database
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
#-------------------------------------------read parameters from BD to initiate
with conn:    
    param = conn.cursor()
    str_sql = 'SELECT NumUnits, NumSp, NumProduct, NumMillProduct, NumMarket, NumRegion,'\
                  + ' MaxPeriod, MaxAge, ccAMin, ccAMax, '\
                  + ' MaxRot, MaxCycle, TotalAreaPlt '\
              +' FROM v_Parameters'
    param.execute(str_sql)
    prmlist = param.fetchone()
    param.close()
 
(NumUnits, NumSp, NumProduct, NumMillProduct, NumMarket, NumRegion, \
 MaxPeriod, MaxAge, ccAMin, \
 ccAMax, MaxRot, MaxCycle, TotalAreaPlt) = prmlist
 
cfg.DBParam.NumUnits     = NumUnits
cfg.DBParam.NumSp        = NumSp
cfg.DBParam.NumProduct   = NumProduct
cfg.DBParam.NumMillProduct   = NumMillProduct
cfg.DBParam.NumMarket    = NumMarket
cfg.DBParam.NumRegion    = NumRegion
cfg.DBParam.MaxPeriod    = MaxPeriod
cfg.DBParam.MaxAge       = MaxAge
cfg.DBParam.ccAMin       = ccAMin
cfg.DBParam.ccAMax       = ccAMax
cfg.DBParam.MaxRot       = MaxRot
cfg.DBParam.MaxCycle     = MaxCycle
cfg.DBParam.TotalAreaPlt = TotalAreaPlt

# -----------InitialArea: Actual Situation of Management Units with their data
cfg.inaDic = {}
inac = conn.cursor()
inac.execute('SELECT u, c, r, sp, a, region FROM V_InitialArea order by 1,2,3,4,5')
for (u, c, r, sp, a, region) in inac:
    cfg.inaDic[u] = (c, r, sp, a, region)
inac.close()

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

# ----------------------------------------------Print Parameters in a text list 
ParamList = CreateParamList()
print_list(ParamList,"Plt2_Parameters.txt"," ")

# ----------------------------------------------Call show Results window
ShowResults('Plt2_ShowResults.ui',MyApp, conn)  

dbResults.close() 
MyApp.quit()  
conn.close() 


#end Plt2_Main      
