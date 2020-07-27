# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 11:54:33 2018

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
import cfg

from Plt2_Results     import *
from Plt2_SimpleModel import *
from Plt2_SuppRun     import *

def RunPareto(conn,MaxIntP):
    
    optPlt2 = SolverFactory(cfg.gvDic['MySolver'])
    #---------------------------------------------------------------------------
    #------------------------------------------------generate the abstract model
    print_str('Building abstract model')
    SendToLog('RunPareto','Building abstract model')
    PltBrModel, PltBrData = PltDefinitions(MaxIntP) 
    #---------------------------------------------------------------------------
    #------------------------------------------generate an instance of the model
    print_str('Building Concrete model')
    SendToLog('RunPareto','Create instance model')
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
         SendToLog('RunPareto','Read results from instance model')  
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

         ResultsIRR = 0
         print_str('Saving results for '+ObjChoice)
         SendToLog('RunPareto','Save Results into the database')
         # --------------------------------------------save results into the database
         SaveResults(ObjChoice,ResultsIRR,'Criteria',1) 
         # -------------------------------------save results into a matrix of criteria
         # fill ResultsDic
         SaveMatrix(ObjChoice)
         
         if ObjChoice in ('MaxVolume','MaxRevenue') :
            cfg.MixMatGen = CalculaMixMatGen()
            SaveMixVariables('Plt2_MixVar.xml')
         # MixMatGen is a dictionary as sp index   

    #for ObjChoice in cfg.ObjSelectionL:
    #---------------------------------------------------------------------------
    # -----------------------------------------------calculate the payoff matrix
    #---------------------------------------------------------------------------
    print_str('Preparing Criteria')
    FillCriteriaDic()
    SaveMatrixDic()
    
    #---------------------------------------------------------------------------
    # --------------------------------------------Pareto Frontier
    #---------------------------------------------------------------------------    
    InitCrtParetoDic()
    FillCrtParetoDic()

    print_str('Running Pareto')
    
    #it lasts a lot, I am not printing during tests
    #instance.pprint("Plt2_TextModel.txt")

    
    #CriteriaDic  >>> (iter, var): (goal, BestValue, WorstValue, Range)
    #--------------------------------0    1          2           3
    #CrtParetoDic >>> (var): (order, nLevels, nIntervals, Interval, objective)
    #--------------------------0      1        2           3        4
    #CrtOrderDic  >>> (order):(var)
    # l1, l2, l3, l4  levels of variable 1,2,3 and 4
    
    PlotPoint = 1
    n1 = 0
    #só para duas variáveis
    
    for l1 in range(1,cfg.CrtParetoDic[cfg.CrtOrderDic[1]][1]+1):  #all levels of variable 1
        
       ChangeCrtValue(instance,cfg.CrtOrderDic[1], n1) 
       nVar = 2

       VarChoice = str(cfg.CrtOrderDic[nVar])
       ObjChoice = cfg.CrtParetoDic[VarChoice][4]
           
       DeactivateAllObjectives(instance)
       DeactivateAllParetoConstraints(instance)  
       ActivateObjChoice(instance, ObjChoice)           
       ActivateParetoConstraint(instance,cfg.CrtOrderDic[1])
       results = optPlt2.solve(instance)
       instance.solutions.load_from(results)
       cfg.SolverResults.Status      = str(results.solver.status)
       cfg.SolverResults.Termination = str(results.solver.termination_condition)
       cfg.SolverResults.ReturnCode  = str(results.solver.return_code)        
       if str(cfg.SolverResults.Termination) == 'optimal':
               cfg.SolverResults.xList, cfg.SolverResults.ObjValue = get_var(instance,ObjChoice)
               PlotPoint += 1
               SaveResults(ObjChoice,0,'Pareto_1_2',PlotPoint) 
               print_str(ObjChoice+' PlotPoint_1_2='+str(PlotPoint)+ 'n1 = ('+ str(n1)+')')
       else:
               cfg.SolverResults.xList, cfg.SolverResults.ObjValue = ([],0) 
            
           
       n1 += 1           
    #end for l1        
 
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
        str_sql = "Insert into ResPareto (idResult, idSimulation, Iteration, PlotPoint, Variable, Objective, RunType, Value) "\
                + "select r.idResult, r.idSimulation, r.mcIteration, r.PlotPoint, v.Variable, r.Objective, r.RunType, v.Value "\
                + "  from Results r inner join ResVariable v on v.idResult = r.idResult "\
                + " where r.idSimulation = "+ str(cfg.gvDic['idSimulation']) +" and substr(r.RunType,1,6) = 'Pareto' "\
                + "   and v.Variable in ("+VarInList+") "\
                + " order by r.idResult,  v.Variable "         
        ParetoIns.execute(str_sql)
        ParetoIns.close()   


    #---------------------------------------------------------------------------
    #-------------------------------------------------------------------save Log  
    #---------------------------------------------------------------------------
    print_list(cfg.LogList,"Plt2_LogList.txt",", ") 
    print_str('Saving Log')
    SaveLog() 

    
# end def RunTOffMatrix       
         
         