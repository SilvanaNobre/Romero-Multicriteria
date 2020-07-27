# -*- coding: utf-8 -*-
"""
created on Tue Feb 27 11:55:15 2018
@author: SilvanaNobre
"""

import os
import sqlite3
import numpy
import matplotlib.pyplot as plt
import win32com.client
import pandas as pd
import time
import math

from pandas import ExcelWriter
from operator import itemgetter, attrgetter, methodcaller

from Plt2_Lib          import *
from pyomo.environ     import *
from pyomo.opt         import SolverFactory
from pyomo.opt         import SolverStatus
from pyomo.opt         import TerminationCondition
from pyomo.core        import Objective
from pyomo.core        import Param

import cfg

def get_var(instance,ObjName):
# ----------------------------------------------------------'  
#                                         Decision Variables"
# ----------------------------------------------------------'     
    rx=[]
    for v in instance.component_objects(Var, active=True):
        #print ("Variable",v)
        varobject = getattr(instance, str(v))
        for index in varobject:
            item_rx=(str(v),index,varobject[index].value)
            #print(str(v)," ",index, varobject[index].value) 
            rx.append(item_rx)
    #end for    
# -------------------------------------------------------------- 
    #                                                   Objetive
    # ----------------------------------------------------------
    # instance.MinDevGoal() 
    if   ObjName == 'MaxArea': 
         dobj = instance.MaxArea()
    elif ObjName == 'MaxVolume':
         dobj = instance.MaxVolume()
    elif ObjName == 'MaxPeriod':
         dobj = instance.MaxPeriod()
    elif ObjName == 'MaxFinalStock': 
         dobj = instance.MaxFinalStock()
    elif ObjName == 'MaxRevenue': 
         dobj = instance.MaxRevenue()
    elif ObjName == 'MaxNPV':  
         dobj = instance.MaxNPV()
    elif ObjName == 'MaxMillPrd':  
         dobj = instance.MaxMillPrd()         
    elif ObjName == 'MinIgor':
         dobj = instance.MinIgor()
    elif ObjName == 'MinDevGoal':
         dobj = instance.MinDevGoal()
    elif ObjName == 'MinMktDev':
         dobj = instance.MinMktDev()   
    else: dobj = ' '        
         
    print_str(ObjName + ' = '+str(dobj))     

    return rx, dobj
#def get_var():


#------------------------------------------------------Save Results
def SaveResults(ObjChoice, IRR, RunType, PlotPoint):  
    
   conn = sqlite3.connect(cfg.gvDic['DatabaseFile'])  
   SaveResult = conn.cursor()
   if not(type(cfg.SolverResults.ReturnCode) is int) :
      cfg.SolverResults.ReturnCode = 0 
   str_sql = "  "
   str_sql = "Insert into Results (ResDate, ResDescription, idSimulation, Objective, RunType, PlotPoint, "\
              + "ObjValue, Status, Termination, ReturnCode, discRate, IRR, mcIteration, mcTimberPrice,  "\
              + "mcCarbonPrice, mcProductivity, mcProductivity2, mcProductivity3, "\
              + "mixClone1, mixClone2, mixClone3 ) "\
              + "values ( DateTime() "                +"  ,"\
              + "'"+cfg.gvDic['SimulationTitle']      +"' ,"\
              + str(cfg.gvDic['idSimulation'])        +"  ,"\
              + "'"+ObjChoice                         +"' ,"\
              + "'"+RunType                           +"' ,"\
              + str(PlotPoint)                        +"  ,"\
              + str(cfg.SolverResults.ObjValue)       +"  ,"\
              + "'"+str(cfg.SolverResults.Status)     +"' ,"\
              + "'"+str(cfg.SolverResults.Termination)+"' ,"\
              + str(cfg.SolverResults.ReturnCode)     +"  ,"\
              + str(cfg.OptParam.discRate)            +"  ,"\
              + str(IRR)                              +"  ,"\
              + str(cfg.MCParam.mcIteration)          +"  ,"\
              + str(cfg.MCParam.mcTimberPrice)        +"  ,"\
              + str(cfg.MCParam.mcCarbonPrice)        +"  ,"\
              + str(cfg.MCParam.mcProductivity)       +"  ,"\
              + str(cfg.MCParam.mcProductivity2)      +"  ,"\
              + str(cfg.MCParam.mcProductivity3)      +"  ,"\
              + str(cfg.MixMatGen[1])                 +"  ,"\
              + str(cfg.MixMatGen[2])                 +"  ,"\
              + str(cfg.MixMatGen[3])                 +"  )"
              
   SaveResult.execute(str_sql) 
   cfg.LastIdResult = SaveResult.lastrowid
    
   for row in cfg.SolverResults.xList :
      (ResultVariable,ResultIndex,ResultValue) = row 
      CleanIndex = str(ResultIndex)
      CleanIndex = CleanIndex.replace("'","")
      
      if (ResultVariable in cfg.VarSaveList) and (ResultValue > 0):
   
         SaveVariables = conn.cursor()
         str_sql = "Insert into ResVariable (idResult, Variable, VarIndex, Value) "\
               +"values ("\
               + str(cfg.LastIdResult)+ " , '"\
               + ResultVariable   + "' , '"\
               + CleanIndex + "' , "\
               + str(ResultValue) + " )"
         SaveVariables.execute(str_sql)  
         
      if (ResultVariable == 'xTotalProd') and (ObjChoice ==  'MinIgor'):
          if ResultValue == 0: cfg.ParamIgor = 0
          else: 
             cfg.ParamIgor = cfg.SolverResults.ObjValue / ResultValue
             
          SaveIgorVariable('Plt2_MixVar.xml')
         
   #end for row in cfg.SolverResults.xList
   
   for row in cfg.ParetoList:
      (ResultVariable,ResultValue) = row 
   
      SavePareto = conn.cursor()
      str_sql = "Insert into ResPareto (idResult, Variable, Value) "\
               +"values ("\
               + str(cfg.LastIdResult)+ " , '"\
               + ResultVariable   + "' , "\
               + str(ResultValue) + " )"
      SavePareto.execute(str_sql)   
   #end for Pareto
   conn.commit()
   conn.close()
#end: def save_results
   
def SaveMatrix(ObjChoice):
   
    for row in [ (ResultVariable,ResultIndex,ResultValue) for 
                 (ResultVariable,ResultIndex,ResultValue) in cfg.SolverResults.xList
                 if ResultVariable in cfg.CrtSelectionL] :
        
        (ResultVariable,ResultIndex,ResultValue) = row 
        
        cfg.ResultsDic[(cfg.MCParam.mcIteration,ObjChoice,ResultVariable)] = ResultValue


def FillCriteriaDic():
    
    Goal = cfg.OptParam.goalRate
    
    VarList = []
    # fill CriteriaDic
    for obji in cfg.ObjSelectionL:
        cVar = cfg.ObjectiveDic[obji][0] #variable
        VarList.append(cVar)
        sense = cfg.ObjectiveDic[obji][1] #sense
        
        if cVar != 'xTotalProd':
           KeyList = [(iteri, obji,vari) for (iteri,obji,vari) in cfg.ResultsDic.keys() \
                      if vari == cVar and iteri == cfg.MCParam.mcIteration and \
                         obji != 'MaxVolume']
        else:
           KeyList = [(iteri, obji,vari) for (iteri,obji,vari) in cfg.ResultsDic.keys() \
                      if vari == cVar and iteri == cfg.MCParam.mcIteration ]
            
        ValList = [(keyi,vali) for (keyi,vali) in cfg.ResultsDic.items() if keyi in KeyList] 
        
        if len(ValList) > 0:
           MaxValue = max(ValList, key=itemgetter(1))[1]
           MinValue = min(ValList, key=itemgetter(1))[1]
        else:
           MaxValue = 0
           MinValue = 0
           
        GoalValue = Goal*(MaxValue-MinValue)
        
        if   sense == 'maximize':
           BestValue  = MaxValue
           WorstValue = MinValue
           GoalValue  = MaxValue - GoalValue
        elif sense == 'minimize':
           BestValue  = MinValue 
           WorstValue = MaxValue
           GoalValue  = MinValue + GoalValue
        else:
           BestValue  = MaxValue
           WorstValue = MinValue
           GoalValue  = MaxValue - GoalValue           
            
        RangeValue = math.fabs(BestValue-WorstValue)
        
                
        #-----------------------0-------------1----------2----------3--------
        cfg.CriteriaDic[(cfg.MCParam.mcIteration,cVar)]=(GoalValue,BestValue,WorstValue,RangeValue)
    #end for obji in cfg.ObjSelectionL:   
    
    # fill cfg.MatrixDic
    for objKeys in [(iteri,obji,vari) for (iteri,obji,vari) in cfg.ResultsDic.keys() \
                    if vari in VarList and iteri == cfg.MCParam.mcIteration]:
        (iteri,obji,vari) = objKeys
        vali = cfg.ResultsDic[objKeys]
        if cfg.CriteriaDic[iteri,vari][3] == 0:
           if (vali - cfg.CriteriaDic[iteri,vari][2]) == 0:
               matrixValue = 1
           else:    
               matrixValue = 0
        else: 
            matrixValue = math.fabs(vali - cfg.CriteriaDic[iteri,vari][2])/cfg.CriteriaDic[iteri,vari][3]
        cfg.MatrixDic[objKeys] = (vali, matrixValue)

    #table to the result window
    # first columns > objectives
    if len(cfg.MatrixTableDic.keys()) > 0:
       row = max(cfg.MatrixTableDic.keys(), key=itemgetter(0))[0] + 1
    else:
       row = 0 
    for obji in cfg.ObjSelectionL:
      col = 0
      cfg.MatrixTableDic[row,col] = cfg.MCParam.mcIteration
      col = 1
      cfg.MatrixTableDic[row,col] = obji                        
      col = 2
      
      for vari in VarList:
        if (cfg.MCParam.mcIteration,obji,vari) in cfg.MatrixDic.keys():  
           cfg.MatrixTableDic[row,col] = cfg.MatrixDic[(cfg.MCParam.mcIteration,obji,vari)][1]
        else:
           cfg.MatrixTableDic[row,col] = 0 
        col = col + 1
      row = row + 1
    #end for
    cfg.MatrixTableDic[-1,0] = 'Iteration'    
    cfg.MatrixTableDic[-1,1] = 'Objectives'
    col = 2
    for vari in VarList:
      cfg.MatrixTableDic[-1,col] = vari
      col = col + 1

def FillCrtParetoDic():
    for vari in cfg.CrtSelectionL:
        
        #CriteriaDic  >>> (iter, var): (goal, BestValue, WorstValue, Range)
        #--------------------------------0    1          2           3
        #CrtParetoDic >>> (var): (order, nLevels, nIntervals, Interval, objective)
        #--------------------------0      1        2           3        4
        
        nLevels = cfg.CrtParetoDic[(vari)][1]
        if nLevels < 1: nLevels = 1
        nIntervals = nLevels - 1
        
        Range      = cfg.CriteriaDic[(cfg.MCParam.mcIteration,vari)][3]
        if nIntervals == 0 : 
           Interval = 0
        else:
           Interval   =  Range / nIntervals
           
        cfg.CrtParetoDic[(vari)] = (cfg.CrtParetoDic[(vari)][0],nLevels,nIntervals,Interval,cfg.CrtParetoDic[(vari)][4])
        
    print(cfg.CrtParetoDic)     
        

def CalculaMixMatGen():
    TotalPrd = 0
    Mix = {}
    if cfg.SolverResults.Status == 'ok':
       for row in [(var, index, value) for (var, index, value) in cfg.SolverResults.xList if var == 'xTotalPrdSP']:
           (var, index, value)= row
           TotalPrd += value
       for row in [(var, index, value) for (var, index, value) in cfg.SolverResults.xList if var == 'xTotalPrdSP']:
           (var, index, value)= row
           if TotalPrd == 0: 
              Mix[index]  = 0
           else: 
              Mix[index] = value / TotalPrd
    else:
       for sp in range(1, cfg.DBParam.NumSp+1): Mix[sp] = 0   
     
    return Mix       


def CompleteCriteriaDic(GoalObj):
    # save results from each criterion optimization in a variable cfg.MatrixTableDic
    # -----------------------------------------------------------------------------
    for objKeys in [(iteri,obji,vari) for (iteri,obji,vari) in cfg.ResultsDic.keys() \
                if  vari in cfg.CrtSelectionL \
                and obji == GoalObj \
                and iteri == cfg.MCParam.mcIteration]:
        (iteri,obji,vari) = objKeys
        vali = cfg.ResultsDic[objKeys]
        if cfg.CriteriaDic[iteri,vari][3] == 0: 
            matrixValue = 0
        else: 
            matrixValue = math.fabs(vali - cfg.CriteriaDic[iteri,vari][2])/cfg.CriteriaDic[iteri,vari][3]
            
        cfg.MatrixDic[objKeys] = (vali, matrixValue)

    #prepare table to the result window
    # first columns > objectives

    row = max(cfg.MatrixTableDic.keys(), key=itemgetter(0))[0] + 1
    colCount = len(cfg.CrtSelectionL) + 1
    col = 0
    cfg.MatrixTableDic[row,col] = cfg.MCParam.mcIteration    
    col = 1
    cfg.MatrixTableDic[row,col] = GoalObj

    for col in range(2, colCount+1):
        vari = cfg.MatrixTableDic[-1,col]
        if (cfg.MCParam.mcIteration,GoalObj,vari) in cfg.MatrixDic.keys():
           cfg.MatrixTableDic[row,col]  = cfg.MatrixDic[(cfg.MCParam.mcIteration,GoalObj,vari)][1]
        else:
           cfg.MatrixTableDic[row,col]  = 0 
        col = col + 1
    #end for

def SaveMatrixDic():
    
    conn = sqlite3.connect(cfg.gvDic['DatabaseFile'])
    SaveMatrix = conn.cursor()
    for objKeys in [(iteri,obji,vari) for (iteri,obji,vari) in cfg.MatrixDic.keys()]:
        (iteri,obji,vari) = objKeys
        MatrixSql = "Insert into ResCriteria(idSimulation,Iteration,"\
                + " Objective,Variable,Value,MatrixValue )"\
                + " values (" \
                +  str(cfg.gvDic['idSimulation']) +" ,"\
                +  str(iteri)                     +" ,"\
                +  "'"+obji                       +"' ,"\
                +  "'"+vari                       +"' ,"\
                +  str(cfg.MatrixDic[objKeys][0]) +" ,"\
                +  str(cfg.MatrixDic[objKeys][1]) +" )"
        # print(MatrixSql)        
        SaveMatrix.execute(MatrixSql)
    SaveMatrix.close()
    conn.commit()                


def SendToLog(FunctionName, PointName):
    LogListItem = []
    LogListItem = [0, cfg.gvDic['SimulationTitle'],FunctionName,str(time.ctime()),PointName]
    cfg.LogList.append(LogListItem)
# end def SendToLog


def SaveLog():
    lenLogList = len(cfg.LogList)
    for i in range(0, lenLogList):
        cfg.LogList[i][0] = cfg.LastIdResult
    conn = sqlite3.connect(cfg.gvDic['DatabaseFile'])
    SaveLog = conn.cursor()
    str_sql = 'INSERT INTO CalcLog '\
             + '( idResult, CLSimulation , CLFunction, CLDateTime, ClPoint) VALUES (?,?,?,?,?)'
    SaveLog.executemany(str_sql,cfg.LogList)
    SaveLog.close()
    conn.commit()
    cfg.LogList = []
#end def SaveLog():


def PrintResMatrix(BeforeMatrixIdResult):
    
    con = sqlite3.connect(cfg.gvDic['DatabaseFile'])
    SQLString = "select Termination, Objective, ObjValue, \
            xTotalArea, xTotalProd, xTotalRev, xTotalCst, \
            xTotalNPV, xTotalPrdPP, xTotalStk \
            from v_Tradeoffs where ResDescription = '"
            
    SQLString2 = "' and IdResult > " + str(BeforeMatrixIdResult)
    SQLString3 = " order by idResult"
    
    FileName = cfg.gvDic['SimulationTitle'] + '_' + str(BeforeMatrixIdResult) + '.xlsx'

    SQLString = SQLString + cfg.gvDic['SimulationTitle'] + SQLString2 + SQLString3

    # pd is the pandas object
    # read_sql returns a dataframe
    ResMatrix_df = pd.read_sql(SQLString, con )

    #if os.path.exists(WorkingDirectory+FileName):
    # write a dataframe into an excel sheet 
    writer = ExcelWriter(cfg.gvDic['WorkingDirectory']+FileName, engine='xlsxwriter')
    ResMatrix_df.to_excel(writer, sheet_name='ResMatrix')
    writer.save() 
#end: def PrintResMatrix       


def CalcIRR(DiscRate, rx):  
   
   CashFlow={} 
   CashFlowList=[]
   PeriodList=[]
   pi = 0
   pSet = set()
   isRev = 1
   
   CashFlowVar = [(rvariable, rindex, rvalue) for (rvariable, rindex, rvalue) in rx\
                  if rvariable in ('xCst','xPrdRev','xCrbRev','xLEV') ]

   for (rvariable, rindex, rvalue) in CashFlowVar:
       if rvariable == 'xCst': isRev = -1 
       else: isRev = 1
       if type(rindex) == tuple:
          pi = rindex[0]
       else:
          pi = rindex
       
       if pi in CashFlow:
           CashFlow[pi] += isRev * rvalue
       else:
           CashFlow[pi] = isRev * rvalue
           pSet.add(pi)
           
   for pi in pSet:
       CashFlow[pi] = CashFlow[pi] * ((1.00 + DiscRate)**pi)
       CashFlowList.append(CashFlow[pi]) 
 
   try: 
      ResIRR = numpy.irr(CashFlowList)
   except:   
      ResIRR = 0
      
   if not(ResIRR > 0): ResIRR = 0 
         
   if str(ResIRR) == 'nan': ResIRR = 0      
    
   return ResIRR
#end: def CalcIRR
   
def print_str(toprint):
    print('----------------------------------------------------------------------------')
    print('-------------------------------------------'+str(toprint))
    
    
    #------------------------------------------------function do print a dictionary
def print_dic(toprint, outfilename, delimited):
    outfile = open(outfilename,'w')
    tline = ()    
    ld = len(toprint)
   
    for key in toprint.keys():
        tline = toprint[key]
        dline = str(key) + ": "
        for item in tline:
            dline = dline + str(item) + delimited
        dline = dline + "\n"
        outfile.write(dline)
    outfile.close()
#end def print_dic

#------------------------------------------------------function do print a list
def print_list(toprint, outfilename, delimited):
    outfile = open(outfilename,'w')
    tline = ()    
    ld = len(toprint)
    for litem in toprint:
        dline = ""
        for item in litem:
            dline = dline + str(item) + delimited
        dline = dline + "\n"    
        outfile.write(dline)
    outfile.close()
#end def print_list    

#--------------------------------------------Create a Parameter printable list
def CreateParamList():
    
    ParamList = []
    Param = ' '
    ParamValue = ' '
    ParamLine = ('---','---------------------------------------------------------------------------------------------')

    ParamList.append(ParamLine)
    ParamList.append(('Global Variables','---------------------------------------------------------------------------'))
    ParamList.append(ParamLine)
    for key in cfg.gvDic.keys():
        ParamList.append((key,' = ',str(cfg.gvDic[key])))    

    ParamList.append(ParamLine)
    ParamList.append(('Optimization Parameters','-------------------------------------------') )  
    ParamList.append(ParamLine)
    ParamList.append(('discRate',         ' = ',str(cfg.OptParam.discRate)))
    ParamList.append(('IgorValue',        ' = ',str(cfg.OptParam.IgorValue)))
    ParamList.append(('conRangeProd',     ' = ',str(cfg.OptParam.conRangeProd)))
    ParamList.append(('Period2Flow',      ' = ',str(cfg.OptParam.Period2Flow)))
    ParamList.append(('ProdPcPrevMin',    ' = ',str(cfg.OptParam.ProdPcPrevMin)))
    ParamList.append(('ProdPcPrevMax',    ' = ',str(cfg.OptParam.ProdPcPrevMax)))
    ParamList.append(('conGenMatSecurity',' = ',str(cfg.OptParam.conRangeProd)))
    ParamList.append(('conIgor',          ' = ',str(cfg.OptParam.conIgor)))
    ParamList.append(('GenMatMin',        ' = ',str(cfg.OptParam.GenMatMin)))       
    ParamList.append(('GenMatMax',        ' = ',str(cfg.OptParam.GenMatMax)))       
    ParamList.append(('conMktProd',       ' = ',str(cfg.OptParam.conMktProd)))
    ParamList.append(('conMillPrd',       ' = ',str(cfg.OptParam.conMillPrd)))    
    ParamList.append(('conNDY',           ' = ',str(cfg.OptParam.conNDY)))
    ParamList.append(('Period2Max',       ' = ',str(cfg.OptParam.Period2Max)))
    ParamList.append(('Period2Flow',       ' = ',str(cfg.OptParam.Period2Flow)))
    ParamList.append(('Regulation',       ' = ',str(cfg.OptParam.Regulation)))
    ParamList.append(('rgControlPeriod',  ' = ',str(cfg.OptParam.rgControlPeriod)))
    ParamList.append(('rgControlPcPrev',  ' = ',str(cfg.OptParam.rgControlPcPrev)))
    ParamList.append(('rgLastAgeClass',   ' = ',str(cfg.OptParam.rgLastAgeClass)))
    ParamList.append(('goalRate',         ' = ',str(cfg.OptParam.goalRate)))
    ParamList.append(('mcIterations',     ' = ',str(cfg.OptParam.mcIterations)))

    ParamList.append(ParamLine)
    ParamList.append(('Prescription Writer Parameters','------------------------------------------------------------------'))
    ParamList.append(ParamLine)
    ParamList.append(('ttype, Description, Possible, ','CycleEnd,',' ReStartAge, Plantation, Production, ccAMin, ccAMax'))
    ParamList.append(ParamLine)
    if len(cfg.pwDic)== 0: ReadPwDicFromDB()
    for key in cfg.pwDic.keys():
        ParamList.append((key,' = ',cfg.pwDic[key]))  
        
    ParamList.append(ParamLine)
    ParamList.append(('Database Parameters','-----------------------------------------------------------------------------'))  
    ParamList.append(ParamLine)
    ParamList.append(('NumUnits',' = ',str(cfg.DBParam.NumUnits)))
    ParamList.append(('NumSp',' = ',str(cfg.DBParam.NumSp)))
    ParamList.append(('NumProduct',' = ',str(cfg.DBParam.NumProduct)))    
    ParamList.append(('NumMillProduct',' = ',str(cfg.DBParam.NumMillProduct)))    
    ParamList.append(('NumMarket',' = ',str(cfg.DBParam.NumMarket)))       
    ParamList.append(('NumRegion',' = ',str(cfg.DBParam.NumRegion)))
    ParamList.append(('MaxPeriod',' = ',str(cfg.DBParam.MaxPeriod)))
    ParamList.append(('MaxAge',' = ',str(cfg.DBParam.MaxAge)))
    ParamList.append(('ccAMin',' = ',str(cfg.DBParam.ccAMin)))
    ParamList.append(('ccAMax',' = ',str(cfg.DBParam.ccAMax)))
    ParamList.append(('MaxRot',' = ',str(cfg.DBParam.MaxRot)))
    ParamList.append(('MaxCycle',' = ',str(cfg.DBParam.MaxCycle)))
    ParamList.append(('TotalAreaPlt',' = ',str(cfg.DBParam.TotalAreaPlt)))
    ParamList.append(ParamLine)   
    
    return ParamList  



     