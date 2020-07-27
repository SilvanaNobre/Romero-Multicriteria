# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 12:12:56 2018

@author: Silvana
"""
from pyomo.environ import *
from pyomo         import opt
from pyomo.opt     import SolverFactory
from pyomo.opt     import SolverStatus
from pyomo.opt     import TerminationCondition
from pyomo.opt     import *
from pyomo.core    import Objective
from pyomo.core    import Param
import sqlite3

from Plt2_Results import *
import Plt2_Lib
import cfg


def DeactivateAllObjectives(instance):
    instance.MaxArea.deactivate()
    instance.MaxVolume.deactivate()
    instance.MaxPeriod.deactivate()
    instance.conNDY.deactivate()
    instance.MaxRevenue.deactivate()
    instance.MaxNPV.deactivate()
    instance.MaxFinalStock.deactivate()
    instance.MinIgor.deactivate()
    instance.MaxMillPrd.deactivate()
    instance.MinDevGoal.deactivate()
    instance.MinMktDev.deactivate()
    
def ActivateObjChoice(instance,ObjChoice):
    if   ObjChoice == 'MaxArea'  : 
         instance.MaxArea.activate()
    elif ObjChoice == 'MaxVolume': 
         instance.MaxVolume.activate() 
    elif ObjChoice == 'MaxPeriod': 
         instance.MaxPeriod.activate()
         # NDY can be activated only if the objective is MaxPeriod
         if cfg.OptParam.conNDY == 'yes': instance.conNDY.activate()
    elif ObjChoice == 'MaxRevenue': 
         instance.MaxRevenue.activate()
    elif ObjChoice == 'MaxNPV': 
         instance.MaxNPV.activate()                 
    elif ObjChoice == 'MaxFinalStock': 
         instance.MaxFinalStock.activate()   
    elif ObjChoice == 'MinIgor': 
         instance.MinIgor.activate()      
    elif ObjChoice == 'MaxMillPrd': 
         instance.MaxMillPrd.activate()  
    elif ObjChoice == 'MinMktDev': 
         instance.MinMktDev.activate()          
   
def DeactivateAllParamConstraints(instance):
    instance.conMktProd1.deactivate()
    instance.conMktProd2.deactivate()
    instance.conMillPrd1.deactivate()
    instance.conMillPrd2.deactivate() 
    instance.conRangeProd1.deactivate()
    instance.conRangeProd2.deactivate()
    instance.conGenMat1.deactivate()
    instance.conGenMat2.deactivate()
    instance.conRegulation1.deactivate()
    instance.conRegulation2.deactivate() 
    instance.conIgor.deactivate()


def DeactivateAllParetoConstraints(instance):
    instance.ParetoControlTotalArea.deactivate()
    instance.ParetoControlTotalProd.deactivate()
    instance.ParetoControlTotalPrdPP.deactivate()
    instance.ParetoControlTotalStk.deactivate()
    instance.ParetoControlTotalRev.deactivate()
    instance.ParetoControlTotalNPV.deactivate()
    instance.ParetoControlTotalMill1.deactivate() 
    instance.ParetoControlTotalMktDev.deactivate()     
    instance.ParetoControlTotalIgor.deactivate()    

    
def ActivateParetoConstraint(instance, cvar):
    if   cvar == 'xTotalArea':
         instance.ParetoControlTotalArea.activate()
    elif cvar == 'xTotalProd': 
         instance.ParetoControlTotalProd.activate()
    elif cvar == 'xTotalPrdPP':
         instance.ParetoControlTotalPrdPP.activate()
    elif cvar == 'xTotalStk':
         instance.ParetoControlTotalStk.activate()
    elif cvar == 'xTotalRev':
         instance.ParetoControlTotalRev.activate()
    elif cvar == 'xTotalNPV':
         instance.ParetoControlTotalNPV.activate()
    elif cvar == 'xTotalIgor':        
         instance.ParetoControlTotalIgor.activate() 
    elif cvar == 'xTotalMill1':          
         instance.ParetoControlTotalMill1.activate() 
    elif cvar == 'xTotalMktDev':          
         instance.ParetoControlTotalMktDev.activate()          
    
def ChangeGoalParameters(instance):
    for crtVar in cfg.CrtSelectionL:
      instance.pGoal[crtVar] = cfg.CriteriaDic[cfg.MCParam.mcIteration,crtVar][0]
        
      if cfg.CriteriaDic[cfg.MCParam.mcIteration, crtVar][3] == 0: 
         instance.pCoefCrt[crtVar] = 1
      else:                    
         instance.pCoefCrt[crtVar] = 1/cfg.CriteriaDic[cfg.MCParam.mcIteration,crtVar][3]
         

def ChangeCrtValue(instance,cvar,n):
    #CriteriaDic  >>> (iter, var): (goal, BestValue, WorstValue, Range)
    #--------------------------------0    1          2           3
    #CrtParetoDic >>> (var): (order, nLevels, nIntervals, Interval, objective)
    #--------------------------0      1        2           3         4
    #CrtOrderDic  >>> (order):(var)
    iteration = cfg.MCParam.mcIteration

    if cfg.CriteriaDic[(iteration,cvar)][1] > cfg.CriteriaDic[(iteration,cvar)][2]:
       nextValue = cfg.CriteriaDic[(iteration,cvar)][1] - (n * cfg.CrtParetoDic[cvar][3])
       if nextValue < cfg.CriteriaDic[(iteration,cvar)][2]:
          nextValue = cfg.CriteriaDic[(iteration,cvar)][2]         
    else:
       nextValue = cfg.CriteriaDic[(iteration,cvar)][1] + (n * cfg.CrtParetoDic[cvar][3])
       if nextValue > cfg.CriteriaDic[(iteration,cvar)][2]:
          nextValue = cfg.CriteriaDic[(iteration,cvar)][2]       
          
    if   cvar == 'xTotalArea':
         instance.pParetoArea = nextValue
         
    elif cvar == 'xTotalProd': 
         instance.pParetoProd = nextValue
         
    elif cvar == 'xTotalPrdPP':
         instance.pParetoPrdPP = nextValue
         
    elif cvar == 'xTotalStk':
         instance.pParetoStk = nextValue
         
    elif cvar == 'xTotalRev':
         instance.pParetoRev = nextValue
         
    elif cvar == 'xTotalNPV':
         instance.pParetoNPV = nextValue
         
    elif cvar == 'xTotalIgor':        
         instance.pParetoIgor = nextValue 

    elif cvar == 'xTotalMill1':        
         instance.pParetoMill1 = nextValue 

    elif cvar == 'xTotalMktDev':        
         instance.pParetoMktDev = nextValue          
  
    
def ChangeMixParameters(instance):
    for sp in range(1, cfg.DBParam.NumSp+1):
        GetMixVariables('Plt2_MixVar.xml')
        instance.pMixMatGen[sp] = cfg.MixMatGen[sp]

# a function to support run procedure 
# it is only for this case: pulp
def ChangeIniArea(sce):
    
    conn = sqlite3.connect(DatabaseFile) 
    SceChange = conn.cursor()
    if sce == 1: 
        str_sql = 'Update InitialArea set Area = 200 where idSpecies = 1'
        SceChange.execute(str_sql) 
        str_sql = 'Update InitialArea set Area = 200 where idSpecies = 2'
        SceChange.execute(str_sql)
        str_sql = 'Update InitialArea set Area = 200 where idSpecies = 3'
        SceChange.execute(str_sql)        
    if sce == 2: 
        str_sql = 'Update InitialArea set Area = 100 where idSpecies = 1'
        SceChange.execute(str_sql) 
        str_sql = 'Update InitialArea set Area = 200 where idSpecies = 2'
        SceChange.execute(str_sql)
        str_sql = 'Update InitialArea set Area = 300 where idSpecies = 3'
        SceChange.execute(str_sql)    
    if sce == 3: 
        str_sql = 'Update InitialArea set Area = 100 where idSpecies = 1'
        SceChange.execute(str_sql) 
        str_sql = 'Update InitialArea set Area = 100 where idSpecies = 2'
        SceChange.execute(str_sql)
        str_sql = 'Update InitialArea set Area = 400 where idSpecies = 3'
        SceChange.execute(str_sql)                 
    if sce == 4: 
        str_sql = 'Update InitialArea set Area = 60 where idSpecies = 1'
        SceChange.execute(str_sql) 
        str_sql = 'Update InitialArea set Area = 270 where idSpecies = 2'
        SceChange.execute(str_sql)
        str_sql = 'Update InitialArea set Area = 270 where idSpecies = 3'
        SceChange.execute(str_sql)    
    if sce == 5: 
        str_sql = 'Update InitialArea set Area = 60 where idSpecies = 1'
        SceChange.execute(str_sql) 
        str_sql = 'Update InitialArea set Area = 170 where idSpecies = 2'
        SceChange.execute(str_sql)
        str_sql = 'Update InitialArea set Area = 370 where idSpecies = 3'
        SceChange.execute(str_sql) 
    if sce == 6: 
        str_sql = 'Update InitialArea set Area = 60 where idSpecies = 1'
        SceChange.execute(str_sql) 
        str_sql = 'Update InitialArea set Area = 70 where idSpecies = 2'
        SceChange.execute(str_sql)
        str_sql = 'Update InitialArea set Area = 470 where idSpecies = 3'
        SceChange.execute(str_sql)          
    if sce == 7: 
        str_sql = 'Update InitialArea set Area = 60 where idSpecies = 1'
        SceChange.execute(str_sql) 
        str_sql = 'Update InitialArea set Area = 60 where idSpecies = 2'
        SceChange.execute(str_sql)
        str_sql = 'Update InitialArea set Area = 480 where idSpecies = 3'
        SceChange.execute(str_sql)  
    conn.commit()    
    return    