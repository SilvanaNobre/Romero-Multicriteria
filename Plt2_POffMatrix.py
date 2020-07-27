# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 11:33:07 2018

@author: Usuario
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

from Plt2_Results     import *
from Plt2_SimpleModel import *
from Plt2_SuppRun     import *

def RunPOffMatrix(MaxIntP):
    
    optPlt2 = SolverFactory(cfg.gvDic['MySolver'])
    #---------------------------------------------------------------------------
    #------------------------------------------------generate the abstract model
    print_str('Building abstract model')
    SendToLog('RunTOffMatrix','Building abstract model')
    PltBrModel, PltBrData = PltDefinitions(MaxIntP) 
    #---------------------------------------------------------------------------
    #------------------------------------------generate an instance of the model
    print_str('Building Concrete model')
    SendToLog('RunTOffMatrix','Create instance model')
    instance = PltBrModel.create_instance(PltBrData)  
    print_str('Finish Concrete model')
    #instance.pprint("Plt2_TextModel.txt")
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
         print_str('Solving model for criteria '+ObjChoice)
         SendToLog('RunTOffMatrix','Solve model for crteria '+ObjChoice)  
         results = optPlt2.solve(instance)
         #---------------------------------------------------------------------------
         #--------------------------------------------------get the instance solution
         print_str('Reading results for '+ObjChoice)
         SendToLog('RunTOffMatrix','Read results from instance model')  
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

         #-------------------------------------------------------------------calc IRR
         SendToLog('RunTOffMatrix','Calc IRR')
         ResultsIRR = CalcIRR(cfg.OptParam.discRate,cfg.SolverResults.xList)
         #--------------------------------------------------------------save solution
         #print_list(rx,"Plt2_DecVarValues.txt")
         with open('Plt2_SolverResults.txt', 'w') as f:
             results.write(ostream=f)

         print_str('Saving results for '+ObjChoice)
         SendToLog('RunTOffMatrix','Save Results into the database')
         # --------------------------------------------save results into the database
         SaveResults(ObjChoice,ResultsIRR,'Criteria',1) 
         # -------------------------------------save results into a matrix of criteria
         # fill ResultsDic
         SaveMatrix(ObjChoice)
         
         if ObjChoice in ('MaxVolume','MaxRevenue') :
            # when the system ends the MaxValume calculation 
            cfg.MixMatGen = CalculaMixMatGen()
            SaveMixVariables('Plt2_MixVar.xml')
         # MixMatGen is a dictionary as sp index   

    #for ObjChoice in cfg.ObjSelectionL:
    #---------------------------------------------------------------------------
    # -----------------------------------------------calculate the payoff matrix
    #---------------------------------------------------------------------------
    print_str('Preparing Criteria')
    FillCriteriaDic()

    #--------------------------------------------------------------------------- 
    # -----------------------------------------------Normalized Goal Programming
    #---------------------------------------------------------------------------
    DeactivateAllObjectives(instance)
    instance.MinDevGoal.activate()
    ChangeGoalParameters(instance)
    #---------------------------------------------------------------------------
    #--------------------------------------------solve the instance of the model
    #---------------------------------------------------------------------------
    print_str('Solving Normalized Goal Programming Model' )
    SendToLog('RunTOffMatrix','Solving Normalized Goal Programming Model')  
    results = optPlt2.solve(instance)
    #---------------------------------------------------------------------------
    #--------------------------------------------------get the instance solution
    #---------------------------------------------------------------------------
    print_str('Reading results for Normalized Goal Programming')
    SendToLog('RunTOffMatrix','Reading results from instance model')  
    instance.solutions.load_from(results)
    #---------------------------------------------------------------------------
    #---------------------------------------------------------get general status
    #---------------------------------------------------------------------------
    cfg.SolverResults.Status      = str(results.solver.status)
    cfg.SolverResults.Termination = str(results.solver.termination_condition)
    cfg.SolverResults.ReturnCode  = str(results.solver.return_code)        
         
    if str(cfg.SolverResults.Status) == 'ok':
       cfg.SolverResults.xList, cfg.SolverResults.ObjValue = get_var(instance,'MinDevGoal')
    else:
       cfg.SolverResults.xList, cfg.SolverResults.ObjValue = ([],0) 

    instance.write("Plt2_LpModel.lp")
    instance.write("Plt2_LpModel.mps")
    #-------------------------------------------------------------------calc IRR
    SendToLog('RunTOffMatrix','Calc IRR')
    ResultsIRR = CalcIRR(cfg.OptParam.discRate,cfg.SolverResults.xList)
    #--------------------------------------------------------------save solution
    #print_list(rx,"Plt2_DecVarValues.txt")
    with open('Plt2_SolverResults.txt', 'w') as f:
         results.write(ostream=f)

    print_str('Saving results for Normalized Goal Programming')
    SendToLog('RunTOffMatrix','Save Results into the database')
    #---------------------------------------------------------------------------
    # --------------------------------------------save results into the database
    #---------------------------------------------------------------------------
    SaveResults('MinDevGoal',ResultsIRR,'Goal',1) 
    SaveMatrix('MinDevGoal')
    CompleteCriteriaDic('MinDevGoal')
    SaveMatrixDic()
    #---------------------------------------------------------------------------
    #-------------------------------------------------------------------save Log  
    #---------------------------------------------------------------------------
    print_list(cfg.LogList,"Plt2_LogList.txt",", ") 
    print_str('Saving Log')
    SaveLog() 
    #---------------------------------------------------------------------------
    # ------------------------------------------------generate excel spreadsheet
    #---------------------------------------------------------------------------
    #PrintResMatrix(cfg.BeforeMatrixIdResult)
    
# end def RunTOffMatrix       
         
         