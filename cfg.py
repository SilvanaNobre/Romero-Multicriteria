# -*- coding: utf-8 -*-
"""
Created on Fri May  4 01:28:11 2018

@author: SilvanaNobre
"""
   
global amSet   # set of ages to control in ageClass

global gvDic   #var: (value) ; keys: DatabaseFile, WorkingDirectory, SimulationTitle, MySolver, RunType
global pwDic   #ttype: (trsDescription,Possible,CycleEnd,ReStartAge,Plantation,Production,ccAMin,ccAMax)

global inaDic  # u: (c, r, sp, a, region)
global trsDic  # trs: (trs_prev, u_prev, c_prev, r_prev, sp_prev, ttype, u, c, r, sp)
global prdDic   # (p,CutSp,prdi): list of (trs_prev, p_prev, a_prev, ttype_prev, CutSp, ttype, region, trs, p, a, prdi)
global prdDicP  # (p): list of (trs_prev, p_prev, a_prev, ttype_prev, CutSp, ttype, region, trs, p, a, prdi)

global ageDic  # age: (trs_prev, p_prev, a_prev, ttype_prev, ttype, trs, p, a, u, cfg.inaDic[u][4], CutSpecie, PltSpecies, Node, BeforeEnd) 
global CriteriaDic  # var:(cGoal, cBestValue, cWorstValue, cRange)
global ObjectiveDic # Objective: Var
global ResultsDic   # (iteration, obj, var): ResultValue
global MatrixDic    # (obj, var): (ResultValue, MatrixValue)
global CrtParetoDic # (var): (Order, nLevels, nIntervals, Interval)
global CrtOrderDic  # (order):(var)
global MatrixTableDic
global MixMatGen

global intList          # trs_prev, p_prev, a_prev, ttype, trs, p, a
global FinalNodes       # (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, cutSp, pltSp, Node, BeforeEnd)
global ParetoList
global LogList          # (log)
global prdList
global prdListP
global CompleteIntList  # (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd)
global CriteriaList     # (var) all criterias
global ObjSelectionL    # objective selection by the user
global CrtSelectionL    # criteria related to objective selection by the user
global VarSaveList      # Variable List to save

global OptParam
global DBParam
global MCParam
global SolverResults

global BeforeMatrixIdResult
global LastIdResult
global LastIntPrev
global Calculate

global ParamIgor

amSet = set()

pwDic = {}
inaDic = {}
trsDic = {}
gvDic = {}
prdDic = {}
prdDicP = {}
ageDic = {}
CriteriaDic = {}
ObjectiveDic = {}
ResultsDic = {}
MatrixDic = {}
CrtParetoDic = {}
CrtOrderDic = {}
MatrixTableDic = {}
MixMatGen = {}

intList = []
CompleteIntList = []
FinalNodes = []
ParetoList = []
LogList = []
ConstValues = []
prdList = []
prdListP = []
CriteriaList = []
ObjSelectionL = []
CrtSelectionL = []
VarSaveList = []

FinalNodes = []
CompleteIntList = []

BeforeMatrixIdResult = 0
LastResult = 0
LastIntPrev = 0
Calculate = True
ParamIgor = 0

class ClassOptParam(object):
      def __init__(self, ProdPcPrevMin, ProdPcPrevMax, 
                       GenMatMin, GenMatMax,
                       discRate, IgorValue, goalRate, mcIterations,
                       conMktProd, conMillPrd, conRangeProd,
                       conGenMatSecurity, conIgor,
                       conNDY, rgControlPeriod, 
                       Regulation, rgControlPcPrev, rgLastAgeClass,
                       Period2Max, Period2Flow):
        self.ProdPcPrevMin     = ProdPcPrevMin
        self.ProdPcPrevMax     = ProdPcPrevMax
        self.GenMatMin         = GenMatMin
        self.GenMatMax         = GenMatMax
        self.discRate          = discRate
        self.IgorValue         = IgorValue
        self.goalRate          = goalRate  
        self.mcIterations      = mcIterations
        self.conMktProd        = conMktProd
        self.conMillPrd        = conMillPrd
        self.conRangeProd      = conRangeProd
        self.conGenMatSecurity = conGenMatSecurity
        self.conIgor           = conIgor
        self.conNDY            = conNDY 
        self.rgControlPeriod   = rgControlPeriod 
        self.Regulation        = Regulation
        self.rgControlPcPrev   = rgControlPcPrev
        self.rgLastAgeClass    = rgLastAgeClass
        self.Period2Max        = Period2Max
        self.Period2Flow       = Period2Flow
        
class ClassDBParam(object):
      def __init__(self, NumUnits, NumSp, NumProduct, NumMillProduct, NumMarket, NumRegion, 
                       MaxPeriod, MaxAge, ccAMin, ccAMax, 
                       MaxRot, MaxCycle, TotalAreaPlt):
        self.NumUnits     = NumUnits
        self.NumSp        = NumSp
        self.NumProduct   = NumProduct
        self.NumMillProduct = NumMillProduct
        self.NumMarket    = NumMarket
        self.NumRegion    = NumRegion
        self.MaxPeriod    = MaxPeriod
        self.MaxAge       = MaxAge
        self.ccAMin       = ccAMin
        self.ccAMax       = ccAMax
        self.MaxRot       = MaxRot
        self.MaxCycle     = MaxCycle   
        self.TotalAreaPlt = TotalAreaPlt     
        
class ClassMCParam(object):        
      def __init__(self, mcIteration, mcTimberPrice, mcCarbonPrice, \
                   mcProductivity, mcProductivity2, mcProductivity3):  
        self.mcIteration     = mcIteration  
        self.mcTimberPrice   = mcTimberPrice
        self.mcCarbonPrice   = mcCarbonPrice
        self.mcProductivity  = mcProductivity
        self.mcProductivity2 = mcProductivity2
        self.mcProductivity3 = mcProductivity3
        
class ClassSolverResults(object):
      def __init__(self, srStatus, srTermination, srReturnCode, srObjValue, srxList):
        self.Status      = srStatus
        self.Termination = srTermination
        self.ReturnCode  = srReturnCode
        self.ObjValue    = srObjValue      
        self.xList       = srxList
#------------------------------------------------------------------------------
#-----------------------------------------------------------Init Opt Parameters
#------------------------------------------------------------------------------
ProdPcPrevMin = 1 
ProdPcPrevMax = 1 
GenMatMin = 1
GenMatMax = 1
discRate = 1
IgorValue = 0.5
goalRate = 1
mcIterations = 1

conMktProd = 'no'
conMillPrd = 'no'
conRangeProd = 'no' 
conGenMatSecurity = 'no'
conIgor = 'no'
conNDY = 'no'

rgControlPeriod = 15 
Regulation = 'TotProd'
rgControlPcPrev = 0.10
rgLastAgeClass = 6
Period2Max = 1
Period2Flow = 1

OptParam = ClassOptParam(ProdPcPrevMin, ProdPcPrevMax, 
                       GenMatMin, GenMatMax,
                       discRate, IgorValue, goalRate, mcIterations,
                       conMktProd,conMillPrd, conRangeProd,
                       conGenMatSecurity, conIgor,
                       conNDY, rgControlPeriod, 
                       Regulation, rgControlPcPrev, rgLastAgeClass,
                       Period2Max, Period2Flow)
   
#------------------------------------------------------------------------------
#------------------------------------------------------Init DataBase Parameters
#------------------------------------------------------------------------------
NumUnits = 10
NumSp = 1
NumProduct = 1 
NumMillProduct = 1
NumMarket = 1
NumRegion = 1  
MaxPeriod = 25
MaxAge = 10
ccAMin = 5
ccAMax = 9
MaxRot = 2
MaxCycle = 5
TotalAreaPlt = 1000
   
DBParam = ClassDBParam(NumUnits, NumSp, NumProduct, NumMillProduct, NumMarket, NumRegion,   
                    MaxPeriod, MaxAge, ccAMin, ccAMax, MaxRot, MaxCycle, 
                    TotalAreaPlt)    
     
#---------------------------------------------------------------------------
#-------------------------------------------------Init MonteCarlo Parameters
#---------------------------------------------------------------------------        
mcIteration = 1
mcTimberPrice = 1
mcCarbonPrice = 1
mcProductivity = 1
mcProductivity2 = 1
mcProductivity3 = 1
MCParam = ClassMCParam(mcIteration, mcTimberPrice, mcCarbonPrice, \
                   mcProductivity, mcProductivity2, mcProductivity3)   

#------------------------------------------------------------------------------
#---------------------------------------------------  Init solver Results Class
#------------------------------------------------------------------------------
srStatus = 'ok'
srTermination = 'optimal' 
srReturnCode = 0
srObjValue = 0       
srxList = []
   
SolverResults = ClassSolverResults(srStatus, srTermination, srReturnCode, 
                                   srObjValue, srxList)  

