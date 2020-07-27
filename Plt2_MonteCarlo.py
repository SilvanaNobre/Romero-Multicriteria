# -*- coding: utf-8 -*-
"""
Created on Wed May 30 23:46:33 2018

@author: SilvanaNobre
"""

from pyomo.environ import *
from pyomo         import opt
from pyomo.opt     import SolverFactory
from pyomo.opt     import SolverStatus
from pyomo.opt     import TerminationCondition
from pyomo.opt     import *

from pyomo.core    import Objective
from pyomo.core    import Param

from operator      import itemgetter, attrgetter, methodcaller
import os
import random

from Plt2_Results     import *
from Plt2_SimpleModel import *
from Plt2_SuppRun     import *

def RunMonteCarlo(MaxIntP):
  print_str('Starting Monte Carlo')  
  SendToLog('RunMonteCarlo','Starting Monte Carlo...')  
  optPlt2 = SolverFactory(cfg.gvDic['MySolver'])
  #---------------------------------------------------------------------------
  #------------------------------------------------generate the abstract model
  print_str('Building Abstract Model') 
  SendToLog('RunMonteCarlo','Building Abstract Model')  
  PltBrModel, PltBrData = PltDefinitions(MaxIntP) 
  #---------------------------------------------------------------------------
  print_str('Building Concrete Model')
  SendToLog('RunMonteCarlo','Building Concrete Model') 
  instance = PltBrModel.create_instance(PltBrData)  
  #---------------------------------------------------------------------------
  #---------------------------------- deactivate all parameterized constraints
  DeactivateAllParetoConstraints(instance)
  DeactivateAllParamConstraints(instance)
  #-------------------------------------- activate only the chosen constraints
  if cfg.OptParam.conMktProd == 'yes':
     instance.conMktProd1.activate()
     instance.conMktProd2.activate()

  if cfg.OptParam.conMillPrd == 'yes':
     instance.conMillPrd1.activate()
     instance.conMillPrd2.activate()
        
  if cfg.OptParam.conRangeProd == 'yes': 
     instance.conRangeProd1.activate()
     instance.conRangeProd2.activate()
  if cfg.OptParam.conGenMatSecurity == 'yes': 
     instance.conGenMat1.activate()
     instance.conGenMat2.activate()
  if cfg.OptParam.conIgor == 'yes': 
     instance.conIgor.activate()
     
  #----------------------------------------------------------regulation always
  instance.conRegulation1.activate()
  instance.conRegulation2.activate()
  
  print_str('Reading production parameters from Database')
  SendToLog('RunMonteCarlo','Reading production parameters from Database') 
  ProductionDic = {}
  conn = sqlite3.connect(cfg.gvDic['DatabaseFile'])
  #-------------------------------------------read parameters from BD to initiate
  with conn: 
    ProductionCursor = conn.cursor()
    str_sql = "SELECT ttype, region, sp, cca, product, pProduction FROM v_Production order by 1,2,3"
    ProductionCursor.execute(str_sql)
    for (ttype, region, sp, cca, product, pProduction) in ProductionCursor:
        ProductionDic[(ttype, region, sp, cca, product)] =  pProduction
    ProductionCursor.close()
  conn.close()  
  #-------------------------------------------read parameters from BD to initiate
  
  Iterations = int(cfg.OptParam.mcIterations)
  for i in range(1, Iterations+1):
    print_str('Iteration = '+str(i))  
    SendToLog('RunMonteCarlo','Iteration '+str(i))   

    randomDic = {} 
    mean = 1
    sdev = 0.1
    for spi in range(1, cfg.DBParam.NumSp+1):
      randomDic[spi] = random.normalvariate(mean, sdev) 
      
    cfg.MCParam.mcIteration     = i
    cfg.MCParam.mcTimberPrice   = 0
    cfg.MCParam.mcCarbonPrice   = 0
    cfg.MCParam.mcProductivity  = randomDic[1] 
    cfg.MCParam.mcProductivity2 = randomDic[2]
    cfg.MCParam.mcProductivity3 = randomDic[3]  
    
    #initialize mix and Igor parameters
    GetMixVariables('Plt2_MixVar.xml')
    GetIgorVAriable('Plt2_MixVar.xml')
    
    #alter production instance parameters
    for row in ProductionDic.keys():
        (ttype, region, sp, a, product) = row
        ProdValue = ProductionDic[(ttype, region, sp, a, product)]
        instance.pProduction[ttype,region,sp,a,product]= ProdValue * randomDic[sp]
        #◙print(str(instance.pProduction[ttype,region,sp,a,product]()))
        
    # from the list of Selected Objectives
    for ObjChoice in cfg.ObjSelectionL:
         # -----------------------------------deactivate all objective functions 
         DeactivateAllObjectives(instance)
         # -----------activate only one objective function related to ObjChoice
         ActivateObjChoice(instance,ObjChoice)
         # ------------------------------------------------Update Mix Parameter
         ChangeMixParameters(instance) 
         #---------------------------------------------------------------------------
         #--------------------------------------------solve the instance of the model
         results = optPlt2.solve(instance)
         #---------------------------------------------------------------------------
         #--------------------------------------------------get the instance solution
         instance.solutions.load_from(results)
         #---------------------------------------------------------------------------
         #---------------------------------------------------------get general status
         cfg.SolverResults.Status      = str(results.solver.status)
         cfg.SolverResults.Termination = str(results.solver.termination_condition)
         cfg.SolverResults.ReturnCode  = str(results.solver.return_code)        
         if str(cfg.SolverResults.Status) == 'ok':
            cfg.SolverResults.xList, cfg.SolverResults.ObjValue = get_var(instance,ObjChoice)
         else:
            cfg.SolverResults.xList, cfg.SolverResults.ObjValue = ([],0) 
         # --------------------------------------------save results into the database
         SaveResults(ObjChoice,0,'Criteria',1) 
         # -------------------------------------save results into a matrix of criteria
         # fill ResultsDic
         SaveMatrix(ObjChoice)
         
         if ObjChoice == 'MaxVolume':
            cfg.MixMatGen = CalculaMixMatGen()
            SaveMixVariables('Plt2_MixVar.xml')

         # MixMatGen is a dictionary as sp index 
         
    #for ObjChoice in cfg.ObjSelectionL:
         
    #---------------------------------------------------------------------------
    # -----------------------------------------------calculate the payoff matrix
    #---------------------------------------------------------------------------
    FillCriteriaDic()
    #--------------------------------------------------------------------------- 
    # -----------------------------------------------Normalized Goal Programming
    #---------------------------------------------------------------------------
    DeactivateAllObjectives(instance)
    instance.MinDevGoal.activate()
    ChangeGoalParameters(instance)
    #---------------------------------------------------------------------------
    #--------------------------------------------solve the instance of the model
    results = optPlt2.solve(instance)
    #---------------------------------------------------------------------------
    #--------------------------------------------------get the instance solution
    instance.solutions.load_from(results)
    #---------------------------------------------------------------------------
    #---------------------------------------------------------get general status
    cfg.SolverResults.Status      = str(results.solver.status)
    cfg.SolverResults.Termination = str(results.solver.termination_condition)
    cfg.SolverResults.ReturnCode  = str(results.solver.return_code)        
         
    if str(cfg.SolverResults.Status) == 'ok':
       cfg.SolverResults.xList, cfg.SolverResults.ObjValue = get_var(instance,'MinDevGoal')
    else:
       cfg.SolverResults.xList, cfg.SolverResults.ObjValue = ([],0) 
    #--------------------------------------------------------------save solution
    # --------------------------------------------save results into the database
    SaveResults('MinDevGoal',0,'Goal',1) 
    SaveMatrix('MinDevGoal')
    CompleteCriteriaDic('MinDevGoal')
    
  # end for iteration  

  SaveMatrixDic()   
  SendToLog('RunMonteCarlo','Preparing text SolverResults')  
  print_str('Preparing text SolverResults')
  
  with open('Plt2_SolverResults.txt', 'w') as f:
       results.write(ostream=f)

  # desativado só para os testes ficarem mais rápidos
  # ativar na versão final
  
  #SendToLog('RunMonteCarlo','Preparing text TextModel')  
  #print_str('Preparing text TextModel')
  #instance.pprint("Plt2_TextModel.txt")  

  #SendToLog('RunMonteCarlo','Preparing text LPModel')  
  #print_str('Preparing text LPModel')    
  #instance.write("Plt2_LpModel.lp")
  
  #SendToLog('RunMonteCarlo','Saving Log')  
  #print_str('Saving Log')  
  #print_list(cfg.LogList,"Plt2_LogList.txt",", ") 
  SaveLog()   

# end def RunMonteCarlo       

         
