# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 02:23:58 2019

@author: SilvanaNobre
"""

   def acctMillEfc_rule(model):
       # calculates xMillEfc
       #-----------------
       SendToLog('PltDefinitions','acctMillEfc_rule_gera linhas')
       needKey = []
       for pi in range(1,MaxIntP+1):
           key = (pi)
           needKey.append(key)
       
       k = ()
       pList = []
       for row in cfg.prdListP:
           # xProd[p,sp,prd]
           k, pList = row
           for pi in range(1,cfg.DBParam.MaxPeriod+1):
                   expr = 0
                   expr1 = model.xMillEfc[pi]
                   expr2 = sum(model.x[trs_prev, p_prev, a_prev, ttype, trs, p, a] * \
                           model.pProduction[ttype_prev,region,CutSp,a, prd] * \
                           model.pPrdConversion[region,CutSp,a,prd,1,1] for
                          (trs_prev, p_prev, a_prev, ttype_prev, CutSp, ttype, region, trs, p, a, prd) in pList if p==pi)
                   expr = expr2 == expr1
                   SendToLog('PltDefinitions:acctMillEfc_rule',str(expr1)) 
                   yield  expr   

           needKey.remove(k)
           
       for k in needKey:
           yield  model.xMillEfc[k] == 0 

   model.acctMillEfc = ConstraintList(rule=acctMillEfc_rule, doc='Mill Production Accounting' ) 
