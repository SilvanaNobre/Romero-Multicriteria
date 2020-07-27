# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 11:53:39 2018

@author: SilvanaNobre
"""

#%%
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.opt import SolverStatus
from pyomo.opt import TerminationCondition
from pyomo.core import Objective
from pyomo.core import Param

import os
import cfg

from operator import itemgetter, attrgetter, methodcaller
from Plt2_Results import *
from Plt2_Lib import *

def PltDefinitions(MaxIntP):

   #------------------------------------------------- create of an abstract model
   model = AbstractModel()
   
   # ---------------------------------------------------------------------------#
   # ------------------------------------------------------- sets declaration --#
   # ---------------------------------------------------------------------------#
   SendToLog('PltDefinitions',' sets')
   model.criteria= Set(dimen=1, doc='Criteria')
   def criteria_init(model):
       return (crtItem for crtItem in cfg.CrtSelectionL)
   model.criteria = Set(dimen=1, initialize=criteria_init)
   
   # se use it in pProduction and xAgeClass
   model.a       = Set(doc='Ages',      ordered=True, domain=NonNegativeIntegers)
   def a_init(model):
       IndexAge = max(cfg.DBParam.ccAMax, cfg.DBParam.MaxAge )
       return range(1, IndexAge+2)
   model.a = Set(initialize=a_init)   
   
   model.a0       = Set(doc='Ages from 0',ordered=True, domain=NonNegativeIntegers)
   def a0_init(model):
       IndexAge = max(cfg.DBParam.ccAMax, cfg.DBParam.MaxAge )
       return range(0, IndexAge+2)
   model.a0 = Set(initialize=a0_init)  
   
   model.ageminus  = Set(initialize=cfg.amSet, doc='Age - 1', ordered=True, domain=NonNegativeIntegers)
   
   # if use it in pDemand, pMinContract, conMktProd1, conMktProd2
   model.p       = Set(doc='Periods',   ordered=True, domain=NonNegativeIntegers)
   def p_init(model):
       return range(1, cfg.DBParam.MaxPeriod+1)
   model.p = Set(initialize=p_init)
   
   # xMarket, xProd, acctmarket, acctTodProd
   model.pMaxInt = Set(doc='Periods for all interventions', ordered=True, domain=NonNegativeIntegers)
   def pMaxInt_init(model):
       return range(1, MaxIntP+1)
   model.pMaxInt = Set(initialize=pMaxInt_init)
   
   model.pMaxInt0 = Set(doc='Periods for all interventions', ordered=True, domain=NonNegativeIntegers)
   def pMaxInt0_init(model):
       return range(0, MaxIntP+1)
   model.pMaxInt0 = Set(initialize=pMaxInt0_init)
   
   # conRangeProd1 and conRangeProd2
   model.pminus  = Set(doc='Periods - 1', ordered=True, domain=NonNegativeIntegers)
   def pminus_init(model):
       return range(2, MaxIntP+1)
   model.pminus = Set(initialize=pminus_init)   
   
   # até agora não usei em lugar nenhum
   model.p0      = Set(doc='Periods from 0 on', ordered=True, domain=NonNegativeIntegers)
   def p0_init(model):
       return range(0, cfg.DBParam.MaxPeriod+1)
   model.p0 = Set(initialize=p0_init)
   
   # para usar em NDY
   model.pMax    = Set(doc='Periods from MaxPeriod on', ordered=True, domain=NonNegativeIntegers)
   def pMax_init(model):
       return range(cfg.OptParam.Period2Max, cfg.DBParam.MaxPeriod+1)
   model.pMax = Set(initialize=pMax_init)   
   
   # pProduction
   model.region  = Set(doc='Regions', ordered=True, domain=PositiveIntegers)
   def region_init(model):
       return range(1, cfg.DBParam.NumRegion+1)
   model.region = Set(initialize=region_init)
   
   # pIniArea
   model.u       = Set(doc='Management Units', ordered=True, domain=PositiveIntegers)
   def u_init(model):
       return range(1, cfg.DBParam.NumUnits+1)
   model.u = Set(initialize=u_init)
   
   # pProduction, pDemand, pMinContract, xMarket, xProd
   # acctmarket, conMktProd1, conMktProd2
   # conRangeProd1, conRangeProd2, acctTotProd
   model.sp      = Set(doc='Species',   ordered=True, domain=PositiveIntegers)
   def sp_init(model):
       return range(1, cfg.DBParam.NumSp+1)
   model.sp = Set(initialize=sp_init)

   # pProduction, pDemand, pMinContract, xMarket, xProd, pTransformation
   # acctmarket, conMktProd1, conMktProd2
   # acctTotProd, acctAgeClass
   model.product = Set(dimen=1, doc='Products')
   def product_init(model):
       return range(1, cfg.DBParam.NumProduct+1)
   model.product = Set(initialize=product_init)
   
   # pTransformation
   model.millproduct = Set(dimen=1, doc='Mill Products')
   def millproduct_init(model):
       return range(1, cfg.DBParam.NumMillProduct+1)
   model.millproduct = Set(initialize=millproduct_init)   
   
   
   
   # pDemand, pMinContract, xMarket, 
   # acctmarket, conMktProd1, conMktProd2
   model.market  = Set(dimen=1, doc='Markets')
   def market_init(model):
       return range(1, cfg.DBParam.NumMarket+1)
   model.market = Set(initialize=market_init)
   
   # pProduction
   model.ttype   = Set(dimen=1, doc='Transition types')
   def ttype_init(model):
       TTypeList = []
       for key, item in cfg.pwDic.items():
           if item[1]: TTypeList.append(key)
       return (tTypeItem for tTypeItem in TTypeList)
   model.ttype = Set(dimen=1, initialize=ttype_init)

   # x  
   model.interv  = Set(dimen=7, doc='Interventions'  , ordered=True)
   def interv_init(model):
       return ((trs_prev, p_prev, a_prev, ttype, trs, p, a) for 
               (trs_prev, p_prev, a_prev, ttype, trs, p, a) in cfg.intList)   
   model.interv = Set(dimen=7, initialize=interv_init)  
   

   # ----------------------------------------------------------------------------#
   # ------------------------------------------------------ Params declaration --#
   # ----------------------------------------------------------------------------#
   SendToLog('PltDefinitions',' regular parameter ')

   model.pIniArea    = Param(model.u,
                              doc='Initial Area (ha)',
                              within=Reals, default=0, mutable=True)
   model.pProduction = Param(model.ttype, model.region, model.sp, model.a, model.product, 
                              doc='Production Volume Table (m3/ha)',
                              within=Reals, default=0, mutable=True)
   model.pPrdConversion = Param(model.region, model.sp, model.a, model.product, model.millproduct, model.market,
                                doc='conversion into Mill Products (something/m3)',
                                within=Reals, default=0, mutable=True)
      
   model.pDemand     = Param(model.p, model.sp, model.product, model.market,  
                              doc='Max Volume(m3) Demand per Market ', 
                              within=Reals, default=0, mutable=True)
   model.pMinContract= Param(model.p, model.sp, model.product, model.market,  
                              doc='Min Volume(m3) Contract per Market ', 
                              within=Reals, default=0, mutable=True)
   model.pMillDemand = Param(model.p, model.millproduct, model.market,
                              doc='Max Pulp(t) Demand per Market ', 
                              within=Reals, default=0, mutable=True)
   model.pMillCompromise = Param(model.p, model.millproduct, model.market,
                              doc='Min Pulp(t) to deliver to the mill ', 
                              within=Reals, default=0, mutable=True)   

   model.pPrice      = Param(model.pMaxInt, model.sp, model.product, model.market,  
                              doc='Price (R$/m3)',
                              within=Reals, default=0, mutable=True) 
   model.pLEV        = Param(model.u, 
                              doc='Land Expectation Value (R$/ha)',
                              within=Reals, default=0, mutable=True)
   model.pMktCst     = Param(model.market, 
                              doc='Addicional Market Cost (R$/m3)',
                              within=Reals, default=0, mutable=True)   
   model.pHrvCst     = Param(model.ttype, model.sp, model.product,
                              doc='Harvest Cost (R$/m3)',
                              within=Reals, default=0, mutable=True) 
   model.pSlvCst     = Param(model.ttype, model.sp, model.region, model.a0,
                              doc='Silvicultural Cost (R$/m3)',
                              within=Reals, default=0, mutable=True) 
   model.pParetoArea = Param(doc='total Pareto Area',
                              within=Reals, default=0, mutable=True)
   model.pParetoProd = Param(doc='total Pareto Prod',
                              within=Reals, default=0, mutable=True) 
   model.pParetoPrdPP = Param(doc='total Pareto PrdPP',
                              within=Reals, default=0, mutable=True) 
   model.pParetoStk = Param(doc='total Pareto Stk',
                              within=Reals, default=0, mutable=True) 
   model.pParetoRev = Param(doc='total Pareto Rev',
                              within=Reals, default=0, mutable=True) 
   model.pParetoNPV = Param(doc='total Pareto NPV',
                              within=Reals, default=0, mutable=True) 
   model.pParetoMill1 = Param(doc='total Pareto Mill 1 -Pulp',
                              within=Reals, default=0, mutable=True)
   model.pParetoIgor   = Param(doc='total Pareto Igor',
                              within=Reals, default=0, mutable=True)
   model.pParetoMktDev = Param(doc='total Market Deviation',
                              within=Reals, default=0, mutable=True)   

   
   def pDscRate_init(model, pMaxInt):
       return  1.00/((1.00+cfg.OptParam.discRate)**pMaxInt)      
   model.pDscRate    = Param(model.pMaxInt, doc='Discount Rate ',
                            within=Reals, default=0, mutable=True,
                            initialize=pDscRate_init)
   
   def pGoal_init(model, criteria):
       if cfg.CriteriaDic[(cfg.MCParam.mcIteration,criteria)][3] == 0: 
          return 0 
       else: 
          return cfg.CriteriaDic[(cfg.MCParam.mcIteration,criteria)][0] / cfg.CriteriaDic[(cfg.MCParam.mcIteration,criteria)][3]
   model.pGoal     = Param(model.criteria,
                           doc='Normalized Goals for each criteria ',
                           within=Reals, default=0, mutable=True,
                           initialize=pGoal_init)

   def pCoefCrt_init(model, criteria):
       if cfg.CriteriaDic[(cfg.MCParam.mcIteration,criteria)][3] == 0: 
          return 1
       else: 
          return 1 / cfg.CriteriaDic[(cfg.MCParam.mcIteration,criteria)][3]
   model.pCoefCrt  = Param(model.criteria,
                           doc='Normalized Coeficient for each criteria ',
                           within=Reals, default=0, mutable=True,
                           initialize=pCoefCrt_init)
   
   def pMixMatGen_init(model, sp):
       return cfg.MixMatGen[sp]
   model.pMixMatGen  = Param(model.sp,
                           doc='Mix of Genetic Material ',
                           within=Reals, default=0, mutable=True,
                           initialize=pMixMatGen_init)       
   def pIgor_init(model):
       return cfg.OptParam.IgorValue
   model.pIgor       = Param(doc = 'Proportion of wood out of a desirable mix',
                           within=Reals, default=0, mutable=True,
                           initialize=pIgor_init)


   # ----------------------------------------------------------------------------#
   # --------------------------------------------------- Params inicialization --#
   # ----------------------------------------------------------------------------#
   SendToLog('PltDefinitions',' Database parameters')
   
   dataBR = DataPortal()

   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT u, pIniArea FROM V_InitialArea order by u',
               param=model.pIniArea)
   
   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT ttype, region, sp, cca, product, pProduction FROM v_Production order by 1,2,3',
               param=model.pProduction)
   
   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT region, sp, a, product, millproduct, market, pPrdConversion FROM v_PrdConversion order by 1,2,3,4,5,6',
               param=model.pPrdConversion)
   
   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT pMaxInt, sp, product, market, pPrice FROM v_Price where pMaxInt <= '+str(MaxIntP)+' order by 1,2',
               param=model.pPrice)
   
   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT p, sp, product, market, pDemand FROM v_Demand where p<=(select max(p) from v_Demand) order by 1,2,3,4',
               param=model.pDemand)

   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT p, sp, product, market, pMinContract FROM v_Demand where p<=(select max(p) from v_Demand) order by 1,2,3',
               param=model.pMinContract)
   
   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT p, millproduct, market, pMillDemand FROM v_MillDemand order by 1,2,3',
               param=model.pMillDemand)  
   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT p, millproduct, market, pMillCompromise FROM v_MillCompromise order by 1,2,3',
               param=model.pMillCompromise)     
   
   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT u, pLEV FROM V_InitialArea order by u',
               param=model.pLEV)

   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT market, pMktCst  FROM v_Market order by 1',
               param=model.pMktCst)   

   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT ttype, sp, product, pHrvCst FROM v_HarvCosts order by 1,2,3',
               param=model.pHrvCst) 

   dataBR.load(filename=cfg.gvDic['DatabaseFile'], using='sqlite3',
               query='SELECT ttype, sp, region, a, pSlvCst FROM v_SilvCosts order by 1,2,3,4',
               param=model.pSlvCst) 
   
   # -------------------------------------------------------------------------#
   # ------------------------------------------------------ Var declaration --#
   # -------------------------------------------------------------------------#
   SendToLog('PltDefinitions',' Var declarations')

   # --------------------------------------------------------Decision Variables 
   model.x            = Var(model.interv,
                            doc='Decision Variables (ha)', bounds=(0.0,None),
                            within=Reals, initialize=0.0)

   model.xMarket      = Var(model.pMaxInt, model.sp, model.product, model.market, 
                            doc='Accounting products delivered to markets',
                            bounds=(0.0,None), within=Reals, initialize=0.0)
   
   # ------------------------------------------------------Accounting Variables 
   model.xProd        = Var(model.pMaxInt, model.sp, model.product,
                            doc='Accounting Var Production (m3)', bounds=(0.0,None),
                            within=Reals, initialize=0.0)
   
   model.xPrdRev      = Var(model.pMaxInt, model.sp, model.product, model.market, 
                            doc='Accounting Revenues R$',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   
   model.xMktRev      = Var(model.market, 
                            doc='Accounting Revenues R$',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   
   model.xMillPrd     = Var(model.pMaxInt, model.millproduct, model.market,
                            doc='Accounting Var Mill Production (t)', bounds=(0.0,None),
                            within=Reals, initialize=0.0)
   
   model.xMktCst      = Var(model.pMaxInt, model.sp, model.product, model.market, 
                            doc='Aditional Costs of the markets (R$)',
                            bounds=(0.0,None), within=Reals, initialize=0.0)   
   
   model.xHrvCst      = Var(model.interv, 
                            doc='Harvest Costs of that interv (R$)',
                            bounds=(0.0,None), within=Reals, initialize=0.0)  
   
   model.xSlvCst      = Var(model.interv, 
                            doc='Silvicultural Costs of that interv (R$)',bounds=(0.0,None),
                            within=Reals, initialize=0.0)
   
   model.xAreaSp      = Var(model.pMaxInt0, model.sp, 
                            doc='Accounting Area per p,sp (ha)', bounds=(0.0,None),
                            within=Reals, initialize=0.0)
   
   model.xAgeClass    = Var(model.a, 
                            doc='Area ou Vol per age class of a particular product',
                            bounds=(0.0,None), within=Reals, initialize=0.0)
   
   model.xAgeClassMPrd = Var(model.a, 
                            doc='Total Vol per age class',
                            bounds=(0.0,None), within=Reals, initialize=0.0)   
   
   model.xLEV         = Var(model.pMaxInt, doc='Accounting LEV (R$)',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   
   #--------------------------------------------------------Trade off variables
   model.xTotalArea   = Var(doc='Total Cut Area  (ha) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0)    
   model.xTotalPrdPSP = Var(model.pMaxInt, model.sp,
                            doc='Total Production per period and species (m3) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalPrdSP  = Var(model.sp,
                            doc='Total Production per species (m3) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalPrdP   = Var(model.pMaxInt,
                            doc='Total Production per period (m3) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalMill1  = Var(doc='Total Mill Production (t) product 1 ',
                            bounds=(0.0,None), within=Reals, initialize=0.0)
   model.xTotalProd   = Var(doc='Total Production (m3) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalPrdPP  = Var(doc='Total Production in a Particular Period (m3) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalStk    = Var(doc='Total Final Stock (m3) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0)  
   model.xTotalPrdRev = Var(doc='Total Production Revenue (R$) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalLEV    = Var(doc='Total LEV (R$) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalMktCst = Var(doc='Total Market aditional Costs (R$) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalHrvCst = Var(doc='Total Harvest Costs (R$) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalSlvCst = Var(doc='Total Silvicultural Costs (R$) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0)   
   model.xTotalRev    = Var(doc='Total Revenue (R$) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalCst    = Var(doc='Total Costs (R$) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0)
   model.xTotalNPV    = Var(doc='Net Present Value (R$) ',
                            bounds=(0.0,None), within=Reals, initialize=0.0) 
   
   
   #------------------------------Deviation around the production anual average   
   # IGOR calculation IGOR = 100 * xTotalDevAvgPrd[sp] / xTotalPrdSP[sp]
   #---------------------------------------------------------------------------
   model. xDevPMixPrd   = Var(model.p, model.sp,
                              doc='Accounting Positive deviations from avg production',
                              bounds=(0.0,None), within=Reals, initialize=0.0)
   
   model.xDevNMixPrd    = Var(model.p, model.sp,
                              doc='Accounting Negative deviations from avg production ',
                              bounds=(0.0,None), within=Reals, initialize=0.0)

   model.xTotalDevMixPrd= Var(model.sp,
                              doc='Total Deviation from Avg Production per Species (m3) ',
                              bounds=(0.0,None), within=Reals, initialize=0.0) 
   
   model.xTotalIgor     = Var(doc='Total Deviation from Avg Production (m3) ',
                              bounds=(0.0,None), within=Reals, initialize=0.0)   
   
   #--------------------------------------------Deviation from Risk Mkt Balance  
   model.xDevNMkt       = Var(model.market,
                              doc='Deviation from Market Revenue per year',
                              bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xDevPMkt       = Var(model.market,
                              doc='Deviation from Market Revenue per year',
                              bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalMktDev   = Var(doc='Risk - Market Balance (R$) ',
                              bounds=(0.0,None), within=Reals, initialize=0.0)
  
   
   #-----------------------------------------------Deviation from criteria Goal  
   model.xDevN          = Var(model.criteria, 
                              doc='Deviation from Criteria Goal',
                              bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xDevP          = Var(model.criteria,
                              doc='Deviation from Criteria Goal',
                              bounds=(0.0,None), within=Reals, initialize=0.0) 
   model.xTotalDev        = Var(doc='Total Deviation from all Goals ',
                              bounds=(0.0,None), within=Reals, initialize=0.0)
   


   #xTotalArea, xTotalProd, xTotalPrdPP, xTotalStk, xTotalLEV, xTotalRev 
   # ----------------------------------------------------------------------------#
   # ------------------------------------------------ Constraint Declaration ----#
   # ----------------------------------------------------------------------------#

   #------------------------------------------------------ InitialArea constraints
   #----------------------------------------------- required---------------------#
   def conIna_rule(model):
       SendToLog('PltDefinitions',' conina_rule')       
       # filter all InitialArea nodes, the initial ones
       # for each node, set the decision variable x equal InitialArea area of the unit
       # on InitialArea nodes, the trs (number of the node) is the same number of the unit
       for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a) for
                   (trs_prev, p_prev, a_prev, ttype, trs, p, a) in cfg.intList
                    if ttype == 'ina']:
           (trs_prev, p_prev, a_prev, ttype, trs, p, a) = row
           yield model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] == model.pIniArea[trs] 
        
   model.conIna = ConstraintList(rule=conIna_rule)

   #------------------------------------------------------------- area constraints
   #----------------------------------------------- required---------------------#
   #--Ponto de melhoria: - pode ir para fora do Abstract model
   def conArea_rule(model):
       SendToLog('PltDefinitions','conarea_rule')  
       # for each previous transition node, starting from the 1
       # the "1" previous node is the first node InitialArea previous node
       # the InitialArea nodes have the previous node equal to 0
       for i in range(1, cfg.LastIntPrev + 1):  
           # filter the model.interv (decision variables indexes)
           # using the number of the previous node
           tr_interv = [(trs_prev, p_prev, a_prev, ttype, trs, p, a) for
                        (trs_prev, p_prev, a_prev, ttype, trs, p, a) in cfg.intList
                         if trs_prev == i ] #i = 234
           # order this group of nodes by previous period
           #--Ponto de melhoria: não sortear a lista, achar menor e maior de outro jeito

           # get the first and the last period of this group of nodes 
           len_tr_interv = len(tr_interv)  #12
           if len_tr_interv > 0:
               p_ini = min(tr_interv, key=itemgetter(1))[1] #7
               p_fin = max(tr_interv, key=itemgetter(1))[1] #8
               #from each period of this group of nodes
               for pi in range(p_ini, p_fin+1):   #7 e 8
                   
                   # filter again, now using the period pi, by previous period
                   # to the left hand side
                   pr_interv = [(trs_prev, p_prev, a_prev, ttype, trs, p, a) for
                                (trs_prev, p_prev, a_prev, ttype, trs, p, a) in 
                                 tr_interv if p_prev == pi ]       
                   
                   # filter the original intList
                   # filter by node and period (not the previous ones)
                   # using i and pi
                   # to create the right hand side
                   tr_prev = [(trs_prev, p_prev, a_prev, ttype, trs, p, a) for
                              (trs_prev, p_prev, a_prev, ttype, trs, p, a) in 
                              cfg.intList if p == pi and trs == i ]
                
                   yield sum(model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] for
                                    (trs_prev, p_prev, a_prev, ttype, trs, p, a) in pr_interv) == \
                         sum(model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] for
                                    (trs_prev, p_prev, a_prev, ttype, trs, p, a) in tr_prev)
               #end for pi 
           #end if len   
       #end for i in range  
   #end def conarea_rule    
   model.conArea = ConstraintList(rule=conArea_rule)

   def acctTotArea_rule(model): 
       # Calculates xTotalArea
       #-----------------------------------
       return sum(model.x[interv] for interv in model.interv) \
              == model.xTotalArea
   model.acctTotArea = Constraint(rule=acctTotArea_rule, doc='Total Area ha')
   
   
   def acctAreaSp_rule(model): 
       exprSP = {}
       for spi in model.sp: exprSP[spi]= 0
       for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a) for
                   (trs_prev, p_prev, a_prev, ttype, trs, p, a) in cfg.intList 
                   if p == 0]:
           (trs_prev, p_prev, a_prev, ttype, trs, p, a) = row

           # 9th trs position is species
           # 6th trs position is unit
           spi = cfg.trsDic[trs][9]
           exprSP[spi] = exprSP[spi] + model.pIniArea[cfg.trsDic[trs][6]]
           
       for spi in model.sp:     
           yield  model.xAreaSp[0,spi] == exprSP[spi]
       
       exprSP = {}
       for pi in model.pMaxInt: #it is correct, from period 1 on
           for spi in model.sp: 
               exprSP[pi,spi]= 0
                                  
       for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) for 
                   (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) in cfg.CompleteIntList]:
           # get the species from previous node: forest that is stand 
           (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) = row
           #if this is a Plantation intervention
           if cfg.pwDic[ttype][4]:
              exprSP[p,PltSpecies] = exprSP[p,PltSpecies] + model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] 
           #if this is a Production intervention
           #and if ReStartAge intervention
           if cfg.pwDic[ttype][5] and cfg.pwDic[ttype][3]:
              exprSP[p,CutSpecies] = exprSP[p,CutSpecies] - model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a]   

       for pi in model.pMaxInt:
           for spi in model.sp:
               yield  model.xAreaSp[pi-1,spi] + exprSP[pi,spi] == model.xAreaSp[pi,spi]

   model.acctAreaSp = ConstraintList(rule=acctAreaSp_rule, doc='Total Area per Species ha')   

   #---------------------------------------------------------production accounting
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------#   
   def acctProd_rule(model):
       # calculates xProd
       #-----------------
       # for each previous transition node, starting from the 1
       # the "1" previous node is the first node InitialArea previous node
       # only over production interventions
       # add a new element in a list >> product 
       # repeat the list for each product
       SendToLog('PltDefinitions','acctprod_rule_gera linhas')
       needKey = []
       for pi in range(1,MaxIntP+1):
           for spi in range(1,cfg.DBParam.NumSp+1):
               for prdi in range (1,cfg.DBParam.NumProduct+1):
                   key = (pi,spi,prdi)
                   needKey.append(key)
       
       k = ()
       pList = []
       for row in cfg.prdList:
           # xProd[p,sp,prd]
           k, pList = row
           expr = 0
           expr1 = model.xProd[k[0],k[1],k[2]]
           needKey.remove(k)
           expr2 = 0
           
           expr2 = sum(model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] * \
                       model.pProduction[ttype_prev,region,CutSp,a, prd] for
                   (trs_prev, p_prev, a_prev, ttype_prev, CutSp, ttype, region, trs, p, a, prd) in pList)
           
           expr = expr2 == expr1
           SendToLog('PltDefinitions:acctprod_rule',str(expr1)) 
           yield  expr   
           
       for k in needKey:
            expr1 = model.xProd[k[0],k[1],k[2]]
            expr2 = 0
            expr  = expr2 == expr1
            yield  expr 
           
   model.acctProd = ConstraintList(rule=acctProd_rule, doc='Production Accounting' ) 
   
   def acctTotProd_rule(model):
       # calculates xTotalProd
       #----------------------
       SendToLog('PltDefinitions','acctTotProd_rule') 
       return sum(model.xProd[p,sp,product] for p       in model.p \
                                            for sp      in model.sp \
                                            for product in model.product) \
               == model.xTotalProd
   model.acctTotProd = Constraint(rule=acctTotProd_rule, doc='Total Production m3') 
   
   def acctTotPrdPP_rule(model):  
       # calculates xTotalPrdPP
       #----------------------
       SendToLog('PltDefinitions','acctTotPrdPP_rule') 
       return sum(model.xProd[cfg.OptParam.Period2Max,sp,product] for sp in model.sp \
                                                             for product in model.product)\
              == model.xTotalPrdPP    
   model.acctTotPrdPP = Constraint(rule=acctTotPrdPP_rule, doc='Total Production(m3) of a particulary period = p') 

   def acctTotPrdPSP_rule(model, p, sp):  
       # calculates xTotalPrdPSP[p,sp]
       #----------------------------------
       SendToLog('PltDefinitions','acctTotPrdPSP_rule') 
       return sum(model.xProd[p,sp,product] for product in model.product) \
               == model.xTotalPrdPSP[p,sp]
   model.acctTotPrdPSPP = Constraint(model.p, model.sp, 
                                     rule=acctTotPrdPSP_rule, doc='Total Production m3') 
   def acctTotPrdSP_rule(model,sp):  
       # calculates xTotalPrdSP[sp]
       #----------------------------------       
       SendToLog('PltDefinitions','acctTotPrdSP_rule') 
       return sum(model.xProd[p,sp,product] for p       in model.p if p > cfg.OptParam.Period2Flow \
                                            for product in model.product) \
               == model.xTotalPrdSP[sp]
   model.acctTotPrdSP = Constraint(model.sp, 
                                   rule=acctTotPrdSP_rule, doc='Total Production per species m3') 
   def acctTotPrdP_rule(model,p):  
       # calculates xTotalPrdP[p]
       #----------------------------------           
       SendToLog('PltDefinitions','acctTotPrdP_rule') 
       return sum(model.xProd[p,sp,product] for sp      in model.sp  \
                                            for product in model.product) \
               == model.xTotalPrdP[p]
   model.acctTotPrdP = Constraint(model.p, 
                                  rule=acctTotPrdP_rule, doc='Total Production per period m3') 
   
   
   def acctMillPrd_rule(model):
       # calculates xMillPrd
       #-----------------
       SendToLog('PltDefinitions','acctMillPrd_rule_gera linhas')
       needKey = []
       for pi in range(1,MaxIntP+1):
           key = (pi)
           needKey.append(key)
       
       k = ()
       pList = []
       for row in cfg.prdListP:
           k, pList = row
           for mpi in range(1,cfg.DBParam.NumMillProduct+1):
               for mkti in range(1,cfg.DBParam.NumMarket+1):
                   expr = 0
                   expr1 = model.xMillPrd[k, mpi, mkti]
                   expr2 = sum(model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] * \
                           model.pProduction[ttype_prev,region,CutSp,a, prd] * \
                           model.pPrdConversion[region,CutSp,a,prd,mpi,mkti] for
                          (trs_prev, p_prev, a_prev, ttype_prev, CutSp, ttype, region, trs, p, a, prd) in pList)
                   expr = expr2 == expr1
                   SendToLog('PltDefinitions:acctMillPrd_rule',str(expr1)) 
                   yield  expr   

           needKey.remove(k)
           
       for k in needKey:
           for mpi in range(1,cfg.DBParam.NumMillProduct+1):
               for mkti in range(1,cfg.DBParam.NumMarket+1):
                   expr1 = model.xMillPrd[k, mpi, mkti]
                   expr2 = 0
                   expr  = expr2 == expr1
                   yield  expr 

   model.acctMillPrd = ConstraintList(rule=acctMillPrd_rule, doc='Mill Production Accounting' ) 
   

   def acctTotMillPrd_rule(model):
       # calculates xTotalProd
       #----------------------
       SendToLog('PltDefinitions','acctTotMillPrd_rule') 
       return sum(model.xMillPrd[p,millproduct,market] for p in model.p \
                                             for millproduct in model.millproduct \
                                             for market in model.market) \
               == model.xTotalMill1
   model.acctTotMillPrd = Constraint(rule=acctTotMillPrd_rule, doc='Total Mill1 Production t') 
   

  
   def acctDevMixPrd_rule(model,p,sp):
       # calculates deviation from Mix
       #----------------------------------       
       SendToLog('PltDefinitions','acctDevMixPrd_rule') 
       return model.xTotalPrdPSP[p,sp] - model.xDevPMixPrd[p,sp] + model.xDevNMixPrd[p,sp] \
              ==  model.pMixMatGen[sp] * model.xTotalPrdP[p] 
   model.acctDevMixPrd = Constraint(model.p, model.sp, 
                         rule=acctDevMixPrd_rule, doc='Deviation from mixMatGen production(m3)')     

   def acctTotDevMixPrd_rule(model,sp):  
       # calculates deviation from Mix
       #----------------------------------        
       SendToLog('PltDefinitions','acctTotDevMixPrd_rule') 
       return sum(model.xDevPMixPrd[p,sp] for p in model.p if p > cfg.OptParam.Period2Flow ) +\
              sum(model.xDevNMixPrd[p,sp] for p in model.p if p > cfg.OptParam.Period2Flow ) \
              == model.xTotalDevMixPrd[sp]   
   model.acctTotDevMixPrd = Constraint(model.sp, 
                            rule=acctTotDevMixPrd_rule, doc='Total Deviation from avg production per species m3')  
   
   def acctTotIgor_rule(model):  
       # calculates xTotalIgor
       #----------------------------------        
       SendToLog('PltDefinitions','acctTotIgor_rule') 
       return sum(model.xTotalDevMixPrd[sp] for sp in model.sp) \
              == model.xTotalIgor   
   model.acctTotIgor = Constraint(rule=acctTotIgor_rule, doc='Total Deviation from mix production m3')  


   #-------------------------------------------------------------market accounting
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------#
   def acctMarket_rule(model,p,sp,product):
       # calculates xMarket
       #----------------------------------         
       SendToLog('PltDefinitions','acctmarket_rule')                       
       return sum(model.xMarket[p,sp,product,market] for market in model.market) \
              == model.xProd[p,sp,product]   
   model.acctMarket = Constraint(model.pMaxInt,model.sp,model.product,\
                                 rule=acctMarket_rule, doc='Market Accounting' )    
   
   #------------------------------------------------------------revenue accounting
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------#
   def acctPrdRev_rule(model,pMaxInt,sp,product,market):
       # calculates xPrdRev[pMaxInt,sp,product,market]
       #-----------------------------------------------         
       SendToLog ('PltDefinitions','acctPrdRev_rule') 
       return model.pDscRate[pMaxInt] *\
              model.pPrice[pMaxInt,sp,product,market] * model.xMarket[pMaxInt,sp,product,market] \
              == model.xPrdRev[pMaxInt,sp,product,market]
   model.acctPrdRev = Constraint(model.pMaxInt, model.sp, model.product, model.market,\
                                 rule=acctPrdRev_rule, doc='Production Revenue Accounting')
   
   def acctTotPrdRev_rule(model):  
       # calculates xTotalPrdRev
       #-----------------------------------------------       
       SendToLog('PltDefinitions','acctTotRev_rule') 
       return sum(model.xPrdRev[p,sp,product,market] for p       in model.pMaxInt \
                                                     for sp      in model.sp \
                                                     for product in model.product\
                                                     for market  in model.market)\
              == model.xTotalPrdRev
   model.acctTotPrdRev = Constraint(rule=acctTotPrdRev_rule, doc='Total Revenue m3')
   
   
   def acctMktRev_rule(model,market):
       # calculates xPrdRev[pMaxInt,sp,product,market]
       #-----------------------------------------------         
       SendToLog ('PltDefinitions','acctMktRev_rule') 
       return sum(model.pDscRate[pMaxInt] *\
                  model.pPrice[pMaxInt,sp,product,market] * \
                  model.xMarket[pMaxInt,sp,product,market] for pMaxInt in model.pMaxInt \
                                                           for sp in model.sp \
                                                           for product in model.product)\
              == model.xMktRev[market]
   model.acctMktRev = Constraint(model.market,\
                                 rule=acctMktRev_rule, doc='Market Revenue Accounting')
   
   #------------------------------------------------------------Market deviation #
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------# 

   def acctDevMkt_rule(model,market):
       # calculates deviation from Mix
       #----------------------------------       
       SendToLog('PltDefinitions','acctDevMkt_rule') 
       return model.xMktRev[market] - model.xDevPMkt[market] + model.xDevNMkt[market] \
              ==  284000000
   model.acctDevMkt = Constraint(model.market, 
                      rule=acctDevMkt_rule, doc='Deviation from Market Revenue')       
   
   
   def acctDevMkt_rule(model):  
       # calculates deviation from Market Revenue
       #----------------------------------        
       SendToLog('PltDefinitions','acctDevMkt_rule') 
       return sum(model.xDevPMkt[market] for market in model.market ) +\
              sum(model.xDevNMkt[market] for market in model.market )\
              == model.xTotalMktDev   
   model.acctDevMkt_rule = Constraint(rule=acctDevMkt_rule, doc='Total Deviation from market Revenue')  
      

   #----------------------------------------------------------------LEV accounting
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------#
   def acctLEV_rule(model):
       # calculates model.xLEV[pi]
       #--------------------------------
       SendToLog('PltDefinitions','acctLEV_rule') 
       
       p_ini = min(cfg.FinalNodes, key=itemgetter(5))[5]
       p_max = max(cfg.FinalNodes, key=itemgetter(5))[5] 
                           
       for pi in model.pMaxInt:
         if (pi < p_ini) or (pi > p_max):
           yield model.xLEV[pi] == 0 
         else:
           expr = 0  
           for row in [    (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, cutSp, pltSp, Node, BeforeEnd) \
                       for (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, cutSp, pltSp, Node, BeforeEnd) \
                       in  cfg.FinalNodes \
                       if (pi == p)\
                      ]:
              (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, cutSp, pltSp, Node, BeforeEnd) = row 
              expr = expr + model.pDscRate[p] * \
                            model.pLEV[u] * model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a]
           #end for                
           yield expr == model.xLEV[pi]
       #end for
   model.acctLEV = ConstraintList(rule=acctLEV_rule, doc='LEV Accounting')

   def acctTotLEV_rule(model):  
       # calculates model.xTotalLEV
       #--------------------------------
       SendToLog('PltDefinitions','acctTotLev_rule') 
       return sum(model.xLEV[pMaxInt] for pMaxInt in model.pMaxInt )\
              == model.xTotalLEV
              
   model.acctTotLEV = Constraint(rule=acctTotLEV_rule, doc='Total Revenue m3') 
   
   #----------------------------------------------------------Total Rev accounting
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------#
   def Revenue_rule(model): 
       # calculates xTotalRev
       #----------------------------
       # ainda falta somar carbono
       return model.xTotalRev == model.xTotalPrdRev + model.xTotalLEV 
   model.Revenue = Constraint(rule=Revenue_rule, doc='Total Revenue')
   
   #------------------------------------------------------------------market Costs
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------# 
   def acctMktCst_rule(model,pMaxInt,sp,product,market):
       # calculates xMktCst[pMaxInt,sp,product,market]
       #----------------------------------------------
       SendToLog('PltDefinitions','acctMktCst_rule')        
       return model.pDscRate[pMaxInt] *\
              model.xMarket[pMaxInt,sp,product,market] * model.pMktCst[market] \
              ==    model.xMktCst[pMaxInt,sp,product,market]
              
   model.acctMktCst = Constraint(model.pMaxInt,model.sp,model.product,model.market,\
                                 rule=acctMktCst_rule, doc='Market Cost Calculation' ) 

   def acctTotMktCst_rule(model):  
       # calculates xTotalMktCst
       #----------------------------------------------       
       SendToLog('PltDefinitions','acctTotMktCst_rule') 
       return sum(model.xMktCst[pMaxInt,sp,product,market] for pMaxInt in model.pMaxInt
                                                           for sp      in model.sp
                                                           for product in model.product
                                                           for market  in model.market)\
               == model.xTotalMktCst
   model.acctTotMktCst_rule = Constraint(rule=acctTotMktCst_rule, doc='Total Market Cost R$')      

   #-----------------------------------------------------------------Harvest Costs
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------#  
   def acctHrvCst_rule(model):
       # calculates xHrvCst[trs_prev, p_prev, a_prev, ttype, trs, p, a] 
       #---------------------------------------------------------------
       SendToLog('PltDefinitions','acctHarvCst_rule') 
       # for each intervention node, starting from the 1
       # the "1" previous node is the first node InitialArea previous node
       #Growing Forest over controlPeriod
       for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a) for
                   (trs_prev, p_prev, a_prev, ttype, trs, p, a) in cfg.intList 
                   if p == 0]:
           (trs_prev, p_prev, a_prev, ttype, trs, p, a) = row
           yield  model.xHrvCst[trs_prev, p_prev, a_prev, ttype, trs, p, a] == 0
           
       for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) for 
                   (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) in cfg.CompleteIntList]:
           # get the species from previous node: forest that is stand 
           (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) = row
           #if this is a Production intervention
           if not(cfg.pwDic[ttype][5]):  
               yield  model.xHrvCst[trs_prev, p_prev, a_prev, ttype, trs, p, a] == 0
           else:
               expr = 0
               for prdi in model.product:
                  expr = expr + model.pDscRate[p] * model.pHrvCst[ttype,CutSpecies,prdi] *\
                                model.pProduction[cfg.trsDic[trs_prev][5], cfg.inaDic[u][4] , CutSpecies, a, prdi] *\
                                model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] 
        
               yield  expr ==  model.xHrvCst[trs_prev, p_prev, a_prev, ttype, trs, p, a]            
   model.acctHrvCst = ConstraintList(rule=acctHrvCst_rule, doc='Harvest Costs Accounting' )  
   
   def acctTotHrvCst_rule(model): 
       # calculates xTotalHrvCst
       #---------------------------------------------------------------       
       SendToLog('PltDefinitions','acctTotHrvCst_rule') 
       return sum(model.xHrvCst[interv] for interv in model.interv) \
              == model.xTotalHrvCst
   model.acctTotHvrCst = Constraint(rule=acctTotHrvCst_rule, doc='Total Harvest Cost R$')      
   
   #-----------------------------------------------------------Silvicultural Costs
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------#  
   def acctSlvCst_rule(model):
       # calculates xSlvCst[trs_prev, p_prev, a_prev, ttype, trs, p, a] 
       #---------------------------------------------------------------       
       SendToLog('PltDefinitions','acctSlvCst_rule') 
       # for each intervention node, starting from the 1
       # the "1" previous node is the first node InitialArea previous node
       for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a) for
                   (trs_prev, p_prev, a_prev, ttype, trs, p, a) in cfg.intList 
                   if p == 0]:
           (trs_prev, p_prev, a_prev, ttype, trs, p, a) = row
           yield  model.xSlvCst[trs_prev, p_prev, a_prev, ttype, trs, p, a] == 0

       for row in [(trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) for 
                   (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) in cfg.CompleteIntList]:
           # get the species from previous node: forest that is stand 
           (trs_prev, p_prev, a_prev, ttype, trs, p, a, u, CutSpecies, PltSpecies, Node, BeforeEnd) = row
           # if the previous intervention Re-Start Age
           ttype_prev = cfg.trsDic[trs_prev][5]
           ReStartAge = cfg.pwDic[ttype_prev][3]
           if not ReStartAge: a_ini = a_prev+1
           else:              a_ini = 0
   
           expr = 0
           for ai in range(a_ini,a+1):
              # (p-(a-ai)) is the period when the cost happens
              # pSlvCst params:           ttype,                  sp,         region,         a
              expr = expr + model.pDscRate[(p-(a-ai))] * \
                            model.pSlvCst[cfg.trsDic[trs_prev][5],CutSpecies,cfg.inaDic[u][4],ai] *\
                            model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] 
        
           yield  expr ==  model.xSlvCst[trs_prev, p_prev, a_prev, ttype, trs, p, a]            
   model.acctSlvCst = ConstraintList(rule=acctSlvCst_rule, doc='Silvicultural Costs Accounting' )    
   
   def acctTotSlvCst_rule(model):  
       # calculates xTotalSlvCst
       #---------------------------   
       SendToLog('PltDefinitions','acctTotSlvCst_rule') 
       return sum(model.xSlvCst[interv] for interv in model.interv) \
              == model.xTotalSlvCst
   model.acctTotSlvCst = Constraint(rule=acctTotSlvCst_rule, doc='Total Silvicultural Cost R$')   
   
   #------------------------------------------------------------------total Costs
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------#     
   def Costs_rule(model): 
       # Calulates xTotalCst
       #-----------------------------------
       # carbon is missing
       return model.xTotalCst == model.xTotalHrvCst + model.xTotalMktCst + model.xTotalSlvCst
   model.Costs = Constraint(rule=Costs_rule, doc='Total Revenue')   
   
   #------------------------------------------------------------------Finaly: NPV
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------#  
   def NPV_rule(model): 
       # Calulates xTotalNPV
       #-----------------------------------       
       return model.xTotalNPV == model.xTotalPrdRev + model.xTotalLEV \
              - model.xTotalMktCst - model.xTotalHrvCst - model.xTotalSlvCst
   model.NPV = Constraint(rule=NPV_rule, doc='Net Present Value')   
   # we cannot use the variable xTotalNPV in a maximization line
   # because ir cannnot assume a negative value
   # we must use model.xTotalRev - model.xTotalCst 
   
   
   #-----------------------------------------------------------------------------
   #------------------------------------------------------------Regulation control
   #-----------------------------------------------------------------------------
   

   #--------------------------------area by AgeClass when Period = rgControlPeriod
   # ----------------------------------------------------------------------------#
   #----------------------------------------------- required---------------------#
   def acctAgeClass_rule(model):
       # to get the first case:
       # when the ControlYear happens between two invervetions in the tree
       # produces a dictionary cpl1 that has age as key
    
       for age in cfg.ageDic.keys():
           SendToLog('PltDefinitions:acctAgeClass_rule',str(model.xAgeClass[age]))  
           expr = 0

           if cfg.OptParam.Regulation in ('Area'):
               expr = sum(model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] for 
                                 (trs_prev, p_prev, a_prev, ttype_prev, ttype, trs, p, a, \
                                  u, region, cutSp, pltSp, Node, BeforeEnd) in cfg.ageDic[age])
       
           elif cfg.OptParam.Regulation == 'Prod1':
                expr = sum( model.pProduction[ttype_prev,region,cutSp,age,1] * \
                            model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] for 
                            (trs_prev, p_prev, a_prev, ttype_prev, ttype, trs, p, a, \
                              u, region, cutSp, pltSp, Node, BeforeEnd) in cfg.ageDic[age])
                
           expr = expr - model.xAgeClass[age]
           yield (0, expr, 0 )
           

           # always do for Volume of all products ('TotalProd')
           exprVol = 0         
           expr1 = 0  
           for product in model.product:
               expr1 = sum(model.pProduction[ttype_prev,region,cutSp,age, product] * \
                           model.pPrdConversion[region,cutSp,age,product,1,1] * \
                           model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] for 
                                  (trs_prev, p_prev, a_prev, ttype_prev, ttype, \
                                   trs, p, a, u, region, cutSp, pltSp, Node, BeforeEnd) in cfg.ageDic[age])
               exprVol = exprVol + expr1
               
           exprVol = exprVol - model.xAgeClassMPrd[age]               
           yield (0, exprVol, 0 )
 
       #end for age in sAge    
   #end def acctAgeClass_rule             
   model.acctAgeClass = ConstraintList(rule=acctAgeClass_rule, 
                        doc='Sum Area or_and Volume per AgeClass in a particular period')
   
   def acctTotStk_rule(model):   
       SendToLog ('PltDefinitions','acctTotStk_rule') 
       return sum(model.xAgeClassMPrd[a] for a in model.a) \
              ==  model.xTotalStk
   model.acctTotStk = Constraint(rule=acctTotStk_rule, doc='Total Final Stock m3')
   
   
   #------------------------------------------------------------------------------
   #-----------------------------------------------------parameterized constraints
   #-------- outside, before solving, we activate or deactivate these connstraints
   #------------------------------------------------------------------------------
   #
   #-----------------------------------------------------regulation constraints
   #------------------------------------------------------------------------------
   def conRegulation1_rule(model,age):
       SendToLog ('PltDefinitions','conRegulation1_rule')         
       if cfg.OptParam.Regulation in ('Area','Prod1'):
          return model.xAgeClass[age-1] * (1-cfg.OptParam.rgControlPcPrev)  <= \
                 model.xAgeClass[age] 
       elif cfg.OptParam.Regulation in ('TotProd'): 
          return model.xAgeClassMPrd[age-1] * (1-cfg.OptParam.rgControlPcPrev)  <= \
                 model.xAgeClassMPrd[age]                
   model.conRegulation1 = Constraint(model.ageminus, rule=conRegulation1_rule, \
                                      doc='Regulation Constraint 1')  
   def conRegulation2_rule(model,age):
       SendToLog ('PltDefinitions','conRegulation2_rule')
       if cfg.OptParam.Regulation in ('Area','Prod1'):
          return model.xAgeClass[age] <= \
                 model.xAgeClass[age-1] * (1+cfg.OptParam.rgControlPcPrev)
       elif cfg.OptParam.Regulation in ('TotProd'): 
          return model.xAgeClassMPrd[age] <= \
                 model.xAgeClassMPrd[age-1] * (1+cfg.OptParam.rgControlPcPrev)                 
   model.conRegulation2 = Constraint(model.ageminus,\
                                     rule=conRegulation2_rule,\
                                     doc='Range Production Constraint 2') 
   
   #--------------------production greater than a contract and lower than a demand 
   #------------------------------------------------------------------------------
 
   def conMktProd1_rule(model, p, sp, product, market):
       SendToLog ('PltDefinitions','conMktProd1_rule')
       return model.pMinContract[p,sp,product, market] <= model.xMarket[p,sp,product,market] 

   model.conMktProd1 = Constraint(model.p, model.sp, model.product, model.market,\
                                  rule=conMktProd1_rule, \
                                  doc='Market Production Constraint')  
                      
   def conMktProd2_rule(model, p, sp, product, market):
       SendToLog ('PltDefinitions','conMktProd2_rule')       
       return 0 <= model.xMarket[p,sp,product,market] <= model.pDemand[p,sp,product,market]

   model.conMktProd2 = Constraint(model.p, model.sp, model.product, model.market,\
                                  rule=conMktProd2_rule, \
                                  doc='Market Production Constraint') 

   #------------------------------range control production of the main (1) product 
   #------------------------------------------------------------------------------
   def conRangeProd1_rule(model):
       SendToLog ('PltDefinitions','conRangeProd1_rule')   
       for sp in model.sp:
         for p in [p for p in model.pMaxInt if p > cfg.OptParam.Period2Flow]:  
           yield model.xProd[p-1,sp,1] * (1-cfg.OptParam.ProdPcPrevMin)  <= \
                 model.xProd[p,sp,1] 
   model.conRangeProd1 = ConstraintList(rule=conRangeProd1_rule, \
                                    doc='Range Production Constraint 1')  
   def conRangeProd2_rule(model):
       SendToLog ('PltDefinitions','conRangeProd2_rule')  
       for sp in model.sp:
         for p in [p for p in model.pMaxInt if p > cfg.OptParam.Period2Flow]: 
           yield model.xProd[p,sp,1] <= \
                 model.xProd[p-1,sp,1] * (1+cfg.OptParam.ProdPcPrevMax)
   model.conRangeProd2 = ConstraintList(rule=conRangeProd2_rule, \
                                    doc='Range Production Constraint 2')  


   #---------------Mill production greater than a contract and lower than a demand 
   #------------------------------------------------------------------------------
 
   def conMillPrd1_rule(model, p, market):
       SendToLog ('PltDefinitions','conMillPrd1_rule')
       return model.pMillCompromise[p,1, market] <= model.xMillPrd[p,1,market] 

   model.conMillPrd1 = Constraint(model.p, model.market, rule=conMillPrd1_rule, \
                                  doc='Mill Production Constraint 1')  
                      
   def conMillPrd2_rule(model, p, market):
       SendToLog ('PltDefinitions','conMillPrd2_rule')       
       return 0 <= model.xMillPrd[p,1,market] <= model.pMillDemand[p,1,market]

   model.conMillPrd2 = Constraint(model.p, model.market, rule=conMillPrd2_rule, \
                                  doc='Mill Production Constraint 2') 


   #---------------------------------------------Genetic Material Security Control 
   #------------------------------------------------------------------------------
   def conGenMat1_rule(model, p, sp):
       SendToLog ('PltDefinitions','conMatGen1_rule')  
       return model.xAreaSp[p,sp] <= cfg.DBParam.TotalAreaPlt * cfg.OptParam.GenMatMax       
   model.conGenMat1 = Constraint(model.pMaxInt, model.sp,\
                                 rule=conGenMat1_rule, \
                                 doc='Genetic Material Control Constraint 1')  
   def conGenMat2_rule(model, p,sp):
       SendToLog ('PltDefinitions','conMatGen2_rule')        
       return model.xAreaSp[p,sp] >= cfg.DBParam.TotalAreaPlt * cfg.OptParam.GenMatMin          
   model.conGenMat2 = Constraint(model.pMaxInt, model.sp,\
                                 rule=conGenMat2_rule, \
                                 doc='Genetic Material Control Constraint 2')    

       
   #-------------------------------------------------------Igor Genetic regularity 
   #------------------------------------------------------------------------------
   def conIgor_rule(model):  
       # calculates xTotalIgor
       #----------------------------------        
       SendToLog('PltDefinitions','conIgor_rule') 
       return model.xTotalIgor <= model.xTotalProd * model.pIgor
   model.conIgor = Constraint(rule=conIgor_rule, doc='Maximum Deviation from mix production m3')  



   #--------------------------------Non Declining Yield of the main (1) product 
   #---------------------------------------------------------------------------
   def conNDY_rule(model, p,sp):
       SendToLog ('PltDefinitions','conNDY_rule')
       return model.xProd[p,sp,1] <= model.xProd[p+1,sp,1] 
   model.conNDY = Constraint(model.pMax, model.sp, rule=conNDY_rule, \
                             doc='Non Declining Yield')         

   # ----------------------------------------- end of parameterized constraints
   #---------------------------------------------------------------------------


   #------------------------------------------------------------------------------
   #--------------------------------------------------------------criteria control
   #------------------------------------------------------------------------------
   #xTotalArea, xTotalProd, xTotalPrdPP, xTotalStk, xTotalRev, xTotalNPV,xTotalIgor 
   def CriteriaControl_rule(model):  
       for crtVar in cfg.CrtSelectionL:
         if   crtVar == 'xTotalArea':
             yield      model.xTotalArea  + model.xDevN[crtVar] - model.xDevP[crtVar] \
                     == model.pGoal[crtVar] 
         elif crtVar == 'xTotalProd':
             yield      model.xTotalProd  + model.xDevN[crtVar] - model.xDevP[crtVar] \
                     == model.pGoal[crtVar]   
         elif crtVar == 'xTotalPrdPP':
             yield      model.xTotalPrdPP + model.xDevN[crtVar] - model.xDevP[crtVar] \
                     == model.pGoal[crtVar] 
         elif crtVar == 'xTotalStk':
             yield      model.xTotalStk   + model.xDevN[crtVar] - model.xDevP[crtVar] \
                     == model.pGoal[crtVar] 
         elif crtVar == 'xTotalRev':
             yield      model.xTotalRev   + model.xDevN[crtVar] - model.xDevP[crtVar] \
                     == model.pGoal[crtVar] 
         elif crtVar == 'xTotalNPV':
             yield      model.xTotalNPV   + model.xDevN[crtVar] - model.xDevP[crtVar] \
                     == model.pGoal[crtVar] 
         elif crtVar == 'xTotalMill1':
             yield      model.xTotalMill1  + model.xDevN[crtVar] - model.xDevP[crtVar] \
                     == model.pGoal[crtVar]
         elif crtVar == 'xTotalIgor':
             yield      model.xTotalIgor  + model.xDevN[crtVar] - model.xDevP[crtVar] \
                     == model.pGoal[crtVar] 
         elif crtVar == 'xTotalMktDev':
             yield      model.xTotalMktDev  + model.xDevN[crtVar] - model.xDevP[crtVar] \
                     == model.pGoal[crtVar]                      

   model.CriteriaControl = ConstraintList(rule=CriteriaControl_rule, doc='Criteria Control')

   def acctTotDev_rule(model):   
       SendToLog ('PltDefinitions','acctTotDev_rule') 
       expr = 0
       for row in [(obji,VarSense) for (obji,VarSense) in cfg.ObjectiveDic.items() \
                   if obji in cfg.ObjSelectionL]:
         (obji,VarSense) = row 
         (crtVar,Sense) = VarSense
         if Sense == 'minimize':
            expr = expr + model.xDevN[crtVar]*model.pCoefCrt[crtVar]
         else:
            expr = expr + model.xDevP[crtVar]*model.pCoefCrt[crtVar]

       yield expr ==  model.xTotalDev

   model.acctTotDev = ConstraintList(rule=acctTotDev_rule, doc='Total Deviation from Goal') 

   #------------------------------------------------------------------------------
   #--------------------------------------------------------------Pareto control
   #------------------------------------------------------------------------------
   #xTotalArea, xTotalProd, xTotalPrdPP, xTotalStk, xTotalRev, xTotalNPV,xTotalIgor 
   
   def ParetoControlTotalArea_rule(model):  
       return model.xTotalArea  == model.pParetoArea 
   model.ParetoControlTotalArea = Constraint(rule=ParetoControlTotalArea_rule, doc='Pareto xTotalArea')

   def ParetoControlTotalProd_rule(model):  
       return model.xTotalProd  == model.pParetoProd 
   model.ParetoControlTotalProd = Constraint(rule=ParetoControlTotalProd_rule, doc='Pareto xTotalProd')

   def ParetoControlTotalPrdPP_rule(model):
       return model.xTotalPrdPP == model.pParetoPrdPP 
   model.ParetoControlTotalPrdPP = Constraint(rule=ParetoControlTotalPrdPP_rule, doc='Pareto xTotalPrdPP')

   def ParetoControlTotalStk_rule(model):
       return model.xTotalStk   == model.pParetoStk 
   model.ParetoControlTotalStk = Constraint(rule=ParetoControlTotalStk_rule, doc='Pareto xTotalStk')

   def ParetoControlTotalRev_rule(model):
       return model.xTotalRev   == model.pParetoRev 
   model.ParetoControlTotalRev = Constraint(rule=ParetoControlTotalRev_rule, doc='Pareto xTotalRev')

   def ParetoControlTotalNPV_rule(model):
       return model.xTotalPrdRev + model.xTotalLEV \
           - model.xTotalMktCst - model.xTotalHrvCst - model.xTotalSlvCst   == model.pParetoNPV  
   model.ParetoControlTotalNPV = Constraint(rule=ParetoControlTotalNPV_rule, doc='Pareto xTotalNPV')

   def ParetoControlTotalIgor_rule(model):
       return model.xTotalIgor   == model.pParetoIgor 
   model.ParetoControlTotalIgor = Constraint(rule=ParetoControlTotalIgor_rule, doc='Pareto xTotalIgor')   
   
   def ParetoControlTotalMill1_rule(model):
       return model.xTotalMill1   == model.pParetoMill1 
   model.ParetoControlTotalMill1 = Constraint(rule=ParetoControlTotalMill1_rule, doc='Pareto xTotalMill1')   

   def ParetoControlTotalMktDev_rule(model):
       return model.xTotalMktDev   == model.pParetoMktDev 
   model.ParetoControlTotalMktDev = Constraint(rule=ParetoControlTotalMktDev_rule, doc='Pareto xTotalMktRev')  

   #------------------------------------------------------------------------------
   #------------------------------------------------objective funcions definitions
   # outside, before solving, we activate or deactivate the alternative objectives 
   #------------------------------------------------------------------------------
   def MaxArea_rule(model):
       SendToLog('PltDefinitions','Objective rules definition')
       return model.xTotalArea
   model.MaxArea = Objective(rule=MaxArea_rule, sense=maximize)
   
   def MaxVolume_rule(model):
       return model.xTotalProd 
   model.MaxVolume = Objective(rule=MaxVolume_rule, sense=maximize)
   
   def MaxRevenue_rule(model):
       return model.xTotalPrdRev + model.xTotalLEV 
   model.MaxRevenue = Objective(rule=MaxRevenue_rule, sense=maximize)
   
   def MaxNPV_rule(model):
       return model.xTotalPrdRev + model.xTotalLEV \
              - model.xTotalMktCst - model.xTotalHrvCst - model.xTotalSlvCst
   model.MaxNPV = Objective(rule=MaxNPV_rule, sense=maximize)

   def MaxPeriod_rule(model):
       return model.xTotalPrdPP
   model.MaxPeriod = Objective(rule=MaxPeriod_rule, sense=maximize)
   
   def MaxFinalStock_rule(model):
       return model.xTotalStk
   model.MaxFinalStock = Objective(rule=MaxFinalStock_rule, sense=maximize) 

   def MinIgor_rule(model):
       return model.xTotalIgor
   model.MinIgor = Objective(rule=MinIgor_rule, sense=minimize) 

   def MaxMillPrd_rule(model):
       return model.xTotalMill1
   model.MaxMillPrd = Objective(rule=MaxMillPrd_rule, sense=maximize) 
   
   def MinMktDev_rule(model):
       return model.xTotalMktDev
   model.MinMktDev = Objective(rule=MinMktDev_rule, sense=minimize)    
   
   def MinDevGoal_rule(model):
       return model.xTotalDev
   model.MinDevGoal = Objective(rule=MinDevGoal_rule, sense=minimize) 
   
   SendToLog('PltDefinitions','before ending Abstract model generation')
   return model, dataBR

#----- PltDefinitions


#%%