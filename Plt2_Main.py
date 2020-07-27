# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 10:21:20 2017

@author: SilvanaNobre 
"""
from PyQt5 import QtGui
from pyomo.opt        import SolverFactory
from pyomo.opt        import SolverStatus
from pyomo.opt        import TerminationCondition
from pyomo.core       import Objective
from pyomo.core       import Param
from operator         import itemgetter, attrgetter, methodcaller
#from pyomo.environ    import *
from Plt2_Lib         import *
from Plt2_ParamForm   import *
from Plt2_ResultsForm import *
from Plt2_MtxGen      import *
from Plt2_Results     import *
from Plt2_POffMatrix  import *
from Plt2_MonteCarlo  import *
from Plt2_Pareto      import *

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
SendToLog('Main','Set up Parameters - Forms')

#--------------------------------------------initialize optimization parameters  
#---------------------------------------------------------read from an xml file
GetOptVariables('Plt2_OptVar.xml')

#-------------------------------------------Set up pre-programmed criteria list
InitObjectiveDic()
InitCriteriaDic()
InitCrtSelectionL()
#--------------------------------------------initialize Mix of Genetic Material  
GetMixVariables('Plt2_MixVar.xml')
GetIgorVariable('Plt2_MixVar.xml')

#------------------------------------------------------------------------------
#------------------------------ conn is defined as a connection to the database  
#--------------------------------------------------to be used in main procedure
#---------------------------------------------------open connection to database
conn = sqlite3.connect(cfg.gvDic['DatabaseFile'])
#---------------------------------------------------------update all parameters
#---------------------------------------------------------read from a user form
#-------------------------------save all parameters into xml files and database
MyApp = QApplication(sys.argv)
UpdateGlobalVariables('Plt2_GeneralParameters.ui', MyApp, conn)

#---------------------------------------------verify if user cancel the process
print(cfg.Calculate)
if cfg.Calculate :

   print('-------------------------------------------Setting up Parameters - Database')
   SendToLog('Main','Set up Parameters - Database')

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
   cfg.DBParam.NumMillProduct = NumMillProduct
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

   #------------------------------------------------------------------------------
   #-(2)--------------------------------------- Call prescription writer functions
   #------------------------------------------------------------------------------
   print('-------------------------------------------Prescription writer')
   SendToLog('Main','Writing Prescriptions')
   #-------------------------------------------------generate possible transitions 
   #--------------------------------------upon existing stand table (initial area)
   #---it will return
   #---trsDic: generated transition dictionary
   #---altList: initialized alternative ages list
   #---intList: initialized interventions list

   #---yCycle: max Clcle among generated alternatives

   yCycle = trs_gen() 
   cfg.DBParam.MaxCycle = yCycle 
   #--- save transitions in a text file to be checked 
   print_dic (cfg.trsDic,"Plt2_Transitions.txt",", ")

   # -----------------------generate possible alternatives regime and intervention 
   #---------------------------------------------------upon transitions dictionary  
   print('-------------------------------------------Prescription Writer')
   SendToLog('Main','Prescription Writer')   
   alt_gen()
   #--- save transitions alternative ages in a text file to be checked 
   print_list(cfg.altList,"Plt2_AlternativeAges.txt",", ")
   #--- save possible interventions in a text file to be checked 
   print_list(cfg.intList,"Plt2_Interventions.txt",", ")


   #------------------------------------------------------------------------------
   #-(3)------------------------ prepare data structure to support the opt process
   #------------------------------------------------------------------------------
   print('-------------------------------------------Preparing data structures')
   SendToLog('Main','Prepare data structure CompleteInt')
   # ------------------------------------Complete information about interventions
   CompleteInterventions()
   print_list(cfg.CompleteIntList,"Plt2_CompleteInt.txt",", ")

   # ------------------------Create a list od final nodes of the intervention list
   #---------------------------------------and returns the Max intervention Period
   MaxIntP = FindFinalNodes()
   SendToLog('Main','Prepare data structure Final Nodes')
   print_list(cfg.FinalNodes,"Plt2_FinalNodes.txt",", ")

   # -----------------------------------------------------Create dic of Production
   SendToLog('Main','Prepare data structure Production Dic')
   CreateProdDic(MaxIntP)   
   print_dic(cfg.prdDic,"Plt2_prdDic.txt",", ")

   # ----------------------------------------------Create a dictionary of AgeClass 
   SendToLog('PltDefinitions:acctAgeClass_rule','Prepare data structure ageDic') 
   CreateAgeClassDic()
   print_dic(cfg.ageDic,"Plt2_AgeClassList.txt",", ")

   # ----------------------------------------------Print Parameters in a text list 
   ParamList = CreateParamList()
   print_list(ParamList,"Plt2_Parameters.txt"," ")

   #------------------------------------------------------------------- LEV Update
   #------------------------ I have to prepare a special function to calculate LEV
   #-------------------------------------------------- and save into the table LEV
   print('-------------------------------------------Updating LEV')
   LEVc = conn.cursor()
   intTx = int((cfg.OptParam.discRate) * 100)
   SqlStr = 'SELECT l.idRegion, l.LEV FROM LEV l '+\
                ' where l.Tx = '   + str(intTx) +\
                  ' and l.Vp = '   + str((cfg.MCParam.mcTimberPrice * 100)) +\
                  ' and l.Vprd = ' + str((cfg.MCParam.mcProductivity * 100))
   LEVc.execute(SqlStr)
  
   for row in LEVc:
       (reg,LEV) = row
       RegLEVc = conn.cursor()
       RegLEVc.execute('Update InitialArea set LEV = '+str(LEV)+\
                       ' where idRegion ='+str(reg))
   conn.commit()
   LEVc.close()
   RegLEVc.close()
   
   
   cfg.VarSaveList = []
   VarToSave = conn.cursor()
   VarToSave.execute('SELECT Variable FROM Variable where FlagCriteria in (1,2)')
   for row in VarToSave:
         (vari,) = row
         cfg.VarSaveList.append(vari) 
   VarToSave.close() 

   #------------------------------------------------------------------------------
   #-(4)----------------------------- run what user had chosen in gvDic['RunType']
   #------------------------------------------------------------------------------
   print('-------------------------------------------Starting optimization process')
   SendToLog('Main','Start optimization process')
   #--------------------------------------------- Which solver we are going to use
   if cfg.gvDic['RunType'] == 'InitialArea':
      ### variar a iteração, assim vai dar errado
      for sce in range(1,8):
          ChangeIniArea(sce)
          cfg.gvDic['SimulationTitle'] = cfg.gvDic['SimulationTitle'] + ', sce= ' + str(sce) + ' '
          cfg.OptParam.conRangeProd = 'yes'
          RunPOffMatrix(MaxIntP)
      #end for sce

   elif cfg.gvDic['RunType'] == 'PayOffMatrix':    
      RunPOffMatrix(MaxIntP)
   
   elif cfg.gvDic['RunType'] == 'MonteCarlo':    
      RunMonteCarlo(MaxIntP)   
   
   elif cfg.gvDic['RunType'] == 'ParetoFrontier':    
      RunPareto(conn,MaxIntP)
   
   #ShowResults('Plt2_ShowResults.ui',MyApp, conn)   
   
#-end if cfg.Calculate
   
MyApp.quit() 
conn.close()

#end Plt2_Main      

   


    


   