# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 2018

@author: Silvana Nobre
"""
from operator import itemgetter, attrgetter, methodcaller
import xml.etree.ElementTree as ET
import cfg
import sqlite3

#------------------------------------------------------------------------------
#---------------------------------------------------init criteria and atributes 
#------------------------------------------------------------------------------ 
def InitCriteriaDic():
   #global CriteriaDic  # var:(cGoal, cBestValue, cWorstValue, cRangeValue)  
   # melhorar >>> ler do banco de dados
   cfg.CriteriaList = ['xTotalArea', 'xTotalProd', 'xTotalPrdPP', 'xTotalStk', \
                       'xTotalRev', 'xTotalNPV', 'xTotalMill1', 'xTotalIgor','xTotalMktDev']
   for cVar in cfg.CriteriaList:
      cfg.CriteriaDic[(1,cVar)] = (0,0,0,0)
   # starts with Zero, but after all criteria run, in results module, it will be calculated   
      
def InitObjectiveDic():
   # melhorar >>> ler do banco de dados 
   #ObjectiveList = ['MaxArea',    'MaxVolume', 'MaxPeriod', 'MaxFinalStock', \
   #                 'MaxRevenue', 'MaxNPV', 'MinIgor', 'MaxPulp']
   cfg.ObjectiveDic['MaxArea']       = ('xTotalArea'  ,'maximize')   
   cfg.ObjectiveDic['MaxVolume']     = ('xTotalProd'  ,'maximize') 
   cfg.ObjectiveDic['MaxPeriod']     = ('xTotalPrdPP' ,'maximize') 
   cfg.ObjectiveDic['MaxFinalStock'] = ('xTotalStk'   ,'maximize') 
   cfg.ObjectiveDic['MaxRevenue']    = ('xTotalRev'   ,'maximize') 
   cfg.ObjectiveDic['MaxNPV']        = ('xTotalNPV'   ,'maximize')  
   cfg.ObjectiveDic['MinIgor']       = ('xTotalIgor'  ,'minimize') 
   cfg.ObjectiveDic['MaxMillPrd']    = ('xTotalMill1' ,'maximize') 
   cfg.ObjectiveDic['MinMktDev']     = ('xTotalMktDev','minimize')
   
def InitCrtSelectionL():
    cfg.CrtSelectionL = []
    for obji in cfg.ObjSelectionL:
        cfg.CrtSelectionL.append(cfg.ObjectiveDic[obji][0])
        

def InitCrtParetoDic():
    cfg.CrtParetoDic = {}
    # inicializar a partir do que tem na tela
    #                               (Order, nLevels, nIntervals, Interval, objective)
    cfg.CrtParetoDic['xTotalNPV']      = (1,     40,         0,        0,'MaxNPV')
    cfg.CrtParetoDic['xTotalMktDev']   = (2,     40,         0,        0,'MinMktDev')
    
    cfg.CrtOrderDic[1] = 'xTotalNPV'
    cfg.CrtOrderDic[2] = 'xTotalMktDev'    

        
#------------------------------------------------------------------------------
#----------------------------------------------------------parameters functions 
#------------------------------------------------------------------------------    
def GetIgorVariable(mixXmlFile):

   mixTree = ET.parse(mixXmlFile)
   mixRoot = mixTree.getroot()

   for mixItem in mixRoot.findall('IgorVar'):
       cfg.ParamIgor = float(mixItem.find('IgorValue').text)
# end: def GetIgorVariable() 

def GetMixVariables(mixXmlFile):

   mixTree = ET.parse(mixXmlFile)
   mixRoot = mixTree.getroot()
   cfg.MixMatGen = {}

   for mixItem in mixRoot.findall('mixVar'):
       spi = int(mixItem.get('name')[2])
       cfg.MixMatGen[spi] = float(mixItem.find('mixValue').text)
# end: def GetMixVariables() 



def GetGlobalVariables(gvXmlFile):

   gvTree = ET.parse(gvXmlFile)
   gvRoot = gvTree.getroot()
   cfg.gvDic = {}

   for gvItem in gvRoot.findall('gbVar'):
       cfg.gvDic[gvItem.get('name')] = gvItem.find('gbValue').text
# end: def GetGlobalVariables() 

   
def GetOptVariables(optXmlFile):

   optTree = ET.parse(optXmlFile)
   optRoot = optTree.getroot()

   objItem = optRoot.find('objListVar')
   if objItem.get('name') == 'ObjList':   
      ObjListStr = objItem.find('objListValue').text 
      cfg.ObjSelectionL = []
      cfg.ObjSelectionL = ObjListStr.split(',')  
 
   for optItem in optRoot.findall('optVar'):
       if optItem.get('name')        == 'ProdPcPrevMin':
          cfg.OptParam.ProdPcPrevMin =  float(optItem.find('optValue').text)
       elif optItem.get('name')      == 'ProdPcPrevMax':
          cfg.OptParam.ProdPcPrevMax =  float(optItem.find('optValue').text) 
          
       elif optItem.get('name')      == 'GenMatMin':
          cfg.OptParam.GenMatMin     =  float(optItem.find('optValue').text)          
       elif optItem.get('name')      == 'GenMatMax':
          cfg.OptParam.GenMatMax     =  float(optItem.find('optValue').text) 
          
       elif optItem.get('name')      == 'discRate':
          cfg.OptParam.discRate      =  float(optItem.find('optValue').text) 
       elif optItem.get('name')      == 'IgorValue':
          cfg.OptParam.IgorValue     =  float(optItem.find('optValue').text)
       elif optItem.get('name')      == 'goalRate':
          cfg.OptParam.goalRate      =  float(optItem.find('optValue').text) 
       elif optItem.get('name')      == 'mcIterations':
          cfg.OptParam.mcIterations  =  int(optItem.find('optValue').text)          
          
       elif optItem.get('name')          == 'conMktProd':
          cfg.OptParam.conMktProd        =  optItem.find('optValue').text  
       elif optItem.get('name')          == 'conMillPrd':
          cfg.OptParam.conMillPrd        =  optItem.find('optValue').text            
          
       elif optItem.get('name')          == 'conRangeProd':
          cfg.OptParam.conRangeProd      =  optItem.find('optValue').text           
       elif optItem.get('name')          == 'conGenMatSecurity':
          cfg.OptParam.conGenMatSecurity =  optItem.find('optValue').text
       elif optItem.get('name')          == 'conIgor':
          cfg.OptParam.conIgor           =  optItem.find('optValue').text
       elif optItem.get('name')          == 'conNDY':
          cfg.OptParam.conNDY            =  optItem.find('optValue').text           
       elif optItem.get('name')        == 'rgControlPeriod':
          cfg.OptParam.rgControlPeriod =  int(optItem.find('optValue').text)           
       elif optItem.get('name')        == 'Regulation':
          cfg.OptParam.Regulation      =  optItem.find('optValue').text           
       elif optItem.get('name')        == 'rgControlPcPrev':
          cfg.OptParam.rgControlPcPrev =  float(optItem.find('optValue').text)           
       elif optItem.get('name')        == 'rgLastAgeClass':
          cfg.OptParam.rgLastAgeClass  =  int(optItem.find('optValue').text)
       elif optItem.get('name')        == 'Period2Max':  
          cfg.OptParam.Period2Max      =  int(optItem.find('optValue').text)  
       elif optItem.get('name')        == 'Period2Flow':  
          cfg.OptParam.Period2Flow     =  int(optItem.find('optValue').text)            
# end: def GetOptVariables() 

def ReadMatrixFromDB():
    
    cfg.MatrixTableDic[-1,0] = 'Iteration'
    cfg.MatrixTableDic[-1,1] = 'Objective'
    col = 1
    for item in cfg.CrtSelectionL:
        col = col + 1
        cfg.MatrixTableDic[-1,col] = item
        
    conn = sqlite3.connect(cfg.gvDic['DatabaseFile'])
    ReadMatrix = conn.cursor()
    MatrixSql = "Select Iteration,Objective,Variable,Value,MatrixValue "\
              + "  from ResCriteria "\
              + " where idSimulation = " + str(cfg.gvDic['idSimulation'])\
              + " order by Iteration,Objective,Variable"
    ReadMatrix.execute(MatrixSql)
    row = -1
    sIteration = 0
    sObjective = "x"
    for item in ReadMatrix:
        (Iteration, Objective, Variable, Value, MatrixValue) = item
        if (sIteration == Iteration) and (sObjective == Objective):
           col = cfg.CrtSelectionL.index(Variable) + 2
           cfg.MatrixTableDic[row,col] = MatrixValue
        else:    
           row = row + 1
           col = 0
           cfg.MatrixTableDic[row,col] = Iteration    
           col = 1
           cfg.MatrixTableDic[row,col] = Objective
           col = cfg.CrtSelectionL.index(Variable) + 2
           cfg.MatrixTableDic[row,col] = MatrixValue
           sIteration = Iteration
           sObjective = Objective
           
    ReadMatrix.close()
    conn.commit()  
    
def ReadPwDicFromDB():
    conn = sqlite3.connect(cfg.gvDic['DatabaseFile'])
    ReadPw = conn.cursor()
    pwSql = "Select ttype, trsDescription, "\
          +        "Possible, CycleEnd, ReStartAge, Plantation, Production, "\
          +        "ccAMin, ccAMax "\
          + "  from TransitionType "
    ReadPw.execute(pwSql)
    for row in ReadPw:
        (ttype, trsDescription,\
         Possible, CycleEnd, ReStartAge, Plantation, Production,\
         ccAMin, ccAMax) = row
        objKeys = (ttype)
        cfg.pwDic[objKeys] = (trsDescription,\
                              Possible, CycleEnd, ReStartAge, Plantation, Production,\
                              ccAMin, ccAMax) 
    ReadPw.close()
    conn.commit()      


def SaveMixVariables(mixXmlFile):

   mixTree = ET.parse(mixXmlFile)
   mixRoot = mixTree.getroot()
   for mixItem in mixRoot.findall('mixVar'):
       spi = int( mixItem.get('name')[2] )
       mixItem.find('mixValue').text = str(round(cfg.MixMatGen[spi],2))
   mixTree.write(mixXmlFile) 
# end: def SaveGlobalVariables() 
  
   
def SaveIgorVariable(mixXmlFile):

   mixTree = ET.parse(mixXmlFile)
   mixRoot = mixTree.getroot()
   for mixItem in mixRoot.findall('IgorVar'):
       mixItem.find('IgorValue').text = str(round(cfg.ParamIgor,2))
   mixTree.write(mixXmlFile) 
# end: def SaveGlobalVariables()    

def SaveGlobalVariables(gvXmlFile):

   gvTree = ET.parse(gvXmlFile)
   gvRoot = gvTree.getroot()
   for gvItem in gvRoot.findall('gbVar'):
       gvItem.find('gbValue').text = cfg.gvDic[gvItem.get('name')]
       
   gvTree.write(gvXmlFile) 
# end: def SaveGlobalVariables() 


def SaveOptVariables(optXmlFile):

   optTree = ET.parse(optXmlFile)
   optRoot = optTree.getroot()

   ObjListStr = ''
   ObjLen = len(cfg.ObjSelectionL)
   i = 0
   for item in cfg.ObjSelectionL:
       ObjListStr = ObjListStr + item
       i += 1
       if i < ObjLen: ObjListStr = ObjListStr + ','
   
   objItem = optRoot.find('objListVar')
   if objItem.get('name') == 'ObjList':   
      objItem.find('objListValue').text =  ObjListStr

   for optItem in optRoot.findall('optVar'):
       if optItem.get('name')  == 'ProdPcPrevMin':
          optItem.find('optValue').text = str(cfg.OptParam.ProdPcPrevMin)
       elif optItem.get('name')  == 'ProdPcPrevMax':
          optItem.find('optValue').text = str(cfg.OptParam.ProdPcPrevMax)
       elif optItem.get('name')  == 'GenMatMin':
          optItem.find('optValue').text = str(cfg.OptParam.GenMatMin)
       elif optItem.get('name')  == 'GenMatMax':
          optItem.find('optValue').text = str(cfg.OptParam.GenMatMax)  
       elif optItem.get('name')  == 'discRate':
          optItem.find('optValue').text = str(cfg.OptParam.discRate) 
       elif optItem.get('name')  == 'IgorValue':
          optItem.find('optValue').text = str(cfg.OptParam.IgorValue) 
       elif optItem.get('name')  == 'IgorValue':
          optItem.find('optValue').text = str(cfg.OptParam.IgorValue) 
       elif optItem.get('name')  == 'goalRate':
          optItem.find('optValue').text = str(cfg.OptParam.goalRate)   
       elif optItem.get('name')  == 'mcIterations':
          optItem.find('optValue').text = str(int(cfg.OptParam.mcIterations))            
       elif optItem.get('name')  == 'conMktProd':
          optItem.find('optValue').text = cfg.OptParam.conMktProd  
       elif optItem.get('name')  == 'conMillPrd':
          optItem.find('optValue').text = cfg.OptParam.conMillPrd            
       elif optItem.get('name')  == 'conRangeProd':
          optItem.find('optValue').text = cfg.OptParam.conRangeProd  
       elif optItem.get('name')  == 'conGenMatSecurity':
          optItem.find('optValue').text = cfg.OptParam.conGenMatSecurity    
       elif optItem.get('name')  == 'conIgor':
          optItem.find('optValue').text = cfg.OptParam.conIgor           
       elif optItem.get('name')  == 'conNDY':
          optItem.find('optValue').text = cfg.OptParam.conNDY  
       elif optItem.get('name')  == 'rgControlPeriod':
          optItem.find('optValue').text = str(cfg.OptParam.rgControlPeriod)  
       elif optItem.get('name')  == 'Regulation':
          optItem.find('optValue').text = cfg.OptParam.Regulation  
       elif optItem.get('name')  == 'rgControlPcPrev':
          optItem.find('optValue').text = str(cfg.OptParam.rgControlPcPrev)  
       elif optItem.get('name')  == 'rgLastAgeClass':
          optItem.find('optValue').text = str(cfg.OptParam.rgLastAgeClass)  
       elif optItem.get('name')  == 'Period2Max':
          optItem.find('optValue').text = str(cfg.OptParam.Period2Max)    
       elif optItem.get('name')  == 'Period2Flow':
          optItem.find('optValue').text = str(cfg.OptParam.Period2Flow)                     
          
   optTree.write(optXmlFile) 
# end: def SaveOptVariables() 
   
#------------------------------------------------------------------------------
#----------------------------functions to ease access to transition information
#------------------------------------------------------------------------------  
# ttype of a Transition
def get_ttype(tr_key):
    (trs_prev, 
     u_prev, c_prev, r_prev, sp_prev, 
     ttype, 
     u_next, c_next, r_next, sp_next) = cfg.trsDic[tr_key]
    return ttype

# species that is being planted
def get_PltSp(tr_key):
    (trs_prev, 
     u_prev, c_prev, r_prev, sp_prev, 
     ttype, 
     u_next, c_next, r_next, sp_next) = cfg.trsDic[tr_key]
    return sp_next
    
# species that is being cut
def get_CutSp(tr_key):
    (trs_prev, u_prev, c_prev, r_prev, sp_prev, 
     ttype, 
     u_next, c_next, r_next, sp_next) = cfg.trsDic[tr_key]
    return sp_prev

# unit that is being planted
def get_unit(tr_key):
    (trs_prev, 
     u_prev, c_prev, r_prev, sp_prev, 
     ttype, 
     u_next, c_next, r_next, sp_next) = cfg.trsDic[tr_key]
    return u_next        


#------------------------------------------------------------------------------
#--------------------------functions to ease access to intervention information
#------------------------------------------------------------------------------ 

# find the final nodes
def FindFinalNodes():
   PrevSet = set()  
   PrevList = []
   cfg.FinalNodes = []
   maxp = 0
       
   # create a set of interventions that are previous of any other 
   for (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, cutSp, pltSp, Node, BeforeEnd) in cfg.CompleteIntList:
        PrevNode = (trs_prev * 10000)+p_prev
        PrevSet.add(PrevNode)
        
   for item in PrevSet:
       PrevList.append(item)
 
   cfg.FinalNodes = [(trs_prev, p_prev, a_prev, ttype, trs, p, a, u, cutSp, pltSp, Node, BeforeEnd ) for 
                     (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, cutSp, pltSp, Node, BeforeEnd ) in 
                      cfg.CompleteIntList if Node not in PrevList]
   maxp = max(cfg.FinalNodes, key=itemgetter(5))[5]   
   return maxp
   #cfg.FinalNodes.sort(key=lambda tup: (tup[5]))
   # FinalNodes is a global Variable
     
# end def FindFinalNodes  
       
def CompleteInterventions():
   
   # add CutSpecies to the intervl 
   cfg.CompleteIntList = []
   for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a) for
               (trs_prev, p_prev, a_prev, ttype, trs, p, a) in cfg.intList if p > 0]:  
       
       (trs_prev, p_prev, a_prev, ttype, trs, p, a) = row
       # get the species from previous node: forest that is being cut >>> CutSpecies
       u = get_unit(trs)
       CutSpecies = get_CutSp(trs)
       PltSpecies = get_PltSp(trs)
       Node = (10000 * trs) + p
       if  p <= cfg.DBParam.MaxPeriod: BeforeEnd = 1
       else:                           BeforeEnd = 0       
       
       cfg.CompleteIntList.append((trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd))

# def CompleteInterventions

def CreateProdDic(MaxIntP):
   # this dictionary will be used inside the model to create the acctProd constraint and xProd variables
   cfg.prdDic = {}
   cfg.prdDicP = {}
   cfg.prdList = []
   cfg.prdListP = []
   prdItemList = []
   prdItemListP = []
   prdTuple = ()

   for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSp, PltSp, Node, BeforeEnd) for 
               (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSp, PltSp, Node, BeforeEnd) in cfg.CompleteIntList 
                if cfg.pwDic[ttype][5] and  p <= MaxIntP ]:
           
       (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSp, PltSp, Node, BeforeEnd) = row
           
       ttype_prev = get_ttype(trs_prev)
       region     = cfg.inaDic[u][4]
       for prdi in range(1,cfg.DBParam.NumProduct+1): 
           prdItemList  = cfg.prdDic.get((p,CutSp,prdi),None)
           prdItemListP = cfg.prdDicP.get((p),None)
           if prdItemList  == None: prdItemList = []
           if prdItemListP == None: prdItemListP = []
           prdTuple  = (trs_prev, p_prev, a_prev, ttype_prev, CutSp, ttype, region, trs, p, a, prdi)
           prdItemList.append(prdTuple)
           prdItemListP.append(prdTuple)
           
           cfg.prdDic[(p,CutSp,prdi)] = prdItemList
           cfg.prdDicP[(p)] = prdItemListP
           
   for k in cfg.prdDic.keys():
        cfg.prdList.append((k,cfg.prdDic.get(k,None)))

   for k in cfg.prdDicP.keys():
        cfg.prdListP.append((k,cfg.prdDicP.get(k,None)))


# end def CreateProdDic(MaxIntP):

def CreateAgeClassDic():
   # this dictionary will be used in AgeClass control
   IndexAge = max(cfg.DBParam.ccAMax, cfg.DBParam.MaxAge )
   cfg.ageDic = {}
   ageDicItem = ()
   for a in range(1, IndexAge+2):
      cfg.ageDic[a] = []

   #Age1
   #Growing Forest over controlPeriod
   for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) for 
               (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) in cfg.CompleteIntList
                if p_prev < cfg.OptParam.rgControlPeriod and
                   p      > cfg.OptParam.rgControlPeriod and
                cfg.pwDic[cfg.trsDic[trs_prev][5]][4] ]:  #4 is the Plantation Ttype

       (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) = row
       # encontra otipo do anterior
       ttype_prev = get_ttype(trs_prev)
       age =  a - (p - cfg.OptParam.rgControlPeriod) 
       if age >= cfg.OptParam.rgLastAgeClass:
          age =  cfg.OptParam.rgLastAgeClass 
              
       ageDicItem =(trs_prev, p_prev, a_prev, ttype_prev, ttype, trs, p, a, u, cfg.inaDic[u][4], CutSpecies, PltSpecies, Node, BeforeEnd)   
       cfg.ageDic[age].append((ageDicItem)) 

        
   # create a list of finalNodes that happens before ControlYear   
   for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a, u, cutSp, pltSp, Node, BeforeEnd) for 
               (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, cutSp, pltSp, Node, BeforeEnd) in cfg.FinalNodes
                if p < cfg.OptParam.rgControlPeriod]:
       (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, cutSp, pltSp, Node, BeforeEnd) = row
           
       if cfg.pwDic[ttype][3]: #3 is the ReStartAge Ttype
              ax = 0
       else:  ax = a

       age = cfg.OptParam.rgControlPeriod - p + ax
       if age >= cfg.OptParam.rgLastAgeClass:
              age =  cfg.OptParam.rgLastAgeClass 
              
       ttype_prev = get_ttype(trs_prev)
       ageDicItem =(trs_prev, p_prev, a_prev, ttype_prev, ttype, trs, p, a, u, cfg.inaDic[u][4], cutSp, pltSp, Node, BeforeEnd)   
       cfg.ageDic[age].append((ageDicItem)) 
    
   cfg.amSet = set()
   for age in cfg.ageDic.keys():
      if age > 1:
         if len(cfg.ageDic[age]) > 0:
            if len(cfg.ageDic[age-1]) > 0:
               cfg.amSet.add(age)

 




    
    