# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 10:01:31 2018

@author: SilvanaNobre
"""

import os
from operator import itemgetter, attrgetter, methodcaller
import Plt2_Lib 
import cfg

#-----------------------------------------------------------------------------
#------------------------------------------------------------ matrix generator
#-----------------------------------------------------------------------------

#------------(1)-trs_gen():
#-------------------------forest transitions from previous state to next state
#-----------------------------------------------------------------------------
def trs_gen():
    
    PossibleTType = []
    for key, item in cfg.pwDic.items():
        if item[1]: PossibleTType.append(key)
        
    regc = []
    regi = ()
    for key, itemr in cfg.inaDic.items():
        regi = (key,itemr[0],itemr[1],itemr[2],itemr[3])
        regc.append(regi)    

    cfg.intList = []
    cfg.altList = []
    cfg.trsDic = {}     #---transition dictionary
    trs_prev = 0  #---previous transition 
    altt = ()     #---each alternative tuple 
    u_cycle = {}  #---max cycle per each unit dictionary
    
    #--------------------- generate mngt alternatives from Register
    #------------------------------- initilize tree of alternatives 
    #--------------------------------initialize cfg.altList and cfg.intList
    #--------------------------------'ina' nodes
    if cfg.pwDic['ina'][1]:
       for (u, c, r, sp, a) in regc:
           cfg.trsDic[u] = (trs_prev,
                      u, -1, -1, sp,
                      'ina',
                      u,  c,  r, sp )
           #-- reg node is in period = 0
           altt = (u,0,a)
           cfg.altList.append(altt)
        
           intt = (0, 0, 0, 'ina', u,0,a)
           cfg.intList.append(intt)
        
           #-- calculates maximum cycle need for each unit u
           u_cycle[u] = c + int(cfg.DBParam.MaxPeriod/cfg.DBParam.ccAMin) + 1
       #end for row in regc:
    
    # calc MaxCycle to pass to the main program    
    i = max(u_cycle, key=u_cycle.get)
    MaxCycle = u_cycle[i]
    trsdLen = len(cfg.trsDic)

        
    trs_in  = min(cfg.trsDic, key=cfg.trsDic.get)  #1     first node is Unit 1 and node 1
    trs_out = trsdLen + 1 # the first one after register is the first prescription
    while True:
        (trs_prev, u_prev, c_prev, r_prev, sp_prev, ttype, u, c, r, sp) = cfg.trsDic[trs_in]
        
        #--------------------------------------------- first transition rule
        #--------------------------------------------- c, r+1, sp
        #--------------------------------------------- ccs
        if cfg.pwDic['ccs'][1]:
           sp_next = sp
           c_next = c
           r_next = r + 1 
           uMaxCycle = u_cycle[u]
           if (c_next <= uMaxCycle): # if next cycle is less than maxCycle of the unit
              while (r_next <= cfg.DBParam.MaxRot):        
                  cfg.trsDic[trs_out] = (trs_in,
                                   u, c, r, sp,
                                   'ccs',
                                   u, c_next, r_next, sp_next) 
                  trs_out = trs_out + 1
                  r_next = r_next + 1
               #end while
           #end if
        # end if in PossibleTType
        
        #---------------------------------------------second transition rule 
        #---------------------------------------------------------------ccr
        #---------------------------------------------clear cut and renew
        #-------------------------------------- change to species sp = 1
        #--------------------------------------------------c+1, r = 1, 
        if cfg.pwDic['ccr'][1]:
           sp_next = sp
           c_next = c + 1
           r_next = 1 
           uMaxCycle = u_cycle[u] 
           if (c_next <= uMaxCycle):
              cfg.trsDic[trs_out] = (trs_in,
                                u, c, r, sp,
                                'ccr',
                                u, c_next, r_next, sp_next) 
              trs_out = trs_out + 1
           #-end if---------------
        # end if in PossibleTType
        
        #---------------------------------------------thrid rule
        #--------------------------------------------------- th1
        #-------------------------------------------- c, r+1, sp
        if cfg.pwDic['th1'][1]: 
           if ttype in ['ina','cl1','fc1']:
              sp_next = sp
              c_next = c
              r_next = r + 1 
              uMaxCycle = u_cycle[u]
              if (c_next <= uMaxCycle): # if next cycle is less than maxCycle of the unit
                 while (r_next <= cfg.DBParam.MaxRot):        
                    cfg.trsDic[trs_out] = (trs_in,
                                   u, c, r, sp,
                                   'th1',
                                   u, c_next, r_next, sp_next) 
                    trs_out = trs_out + 1
                    r_next = r_next + 1
                 #end while
              #end if
           #end if ttype   
        # end if in PossibleTType
        
        #---------------------------------------------thrid rule
        #--------------------------------------------------- th2
        #-------------------------------------------- c, r+1, sp
        if cfg.pwDic['th2'][1]: 
           if ttype in ['ina','cl2','fc2']:
              sp_next = sp
              c_next = c
              r_next = r + 1 
              uMaxCycle = u_cycle[u]
              if (c_next <= uMaxCycle): # if next cycle is less than maxCycle of the unit
                 while (r_next <= cfg.DBParam.MaxRot):        
                    cfg.trsDic[trs_out] = (trs_in,
                                   u, c, r, sp,
                                   'th2',
                                   u, c_next, r_next, sp_next) 
                    trs_out = trs_out + 1
                    r_next = r_next + 1
                 #end while
              #end if
           #end if ttype   
        # end if in PossibleTType        

        #---------------------------------------------thrid rule
        #--------------------------------------------------- th3
        #-------------------------------------------- c, r+1, sp
        if cfg.pwDic['th3'][1]: 
           if ttype in ['ina','cl3','fc3']:
              sp_next = sp
              c_next = c
              r_next = r + 1 
              uMaxCycle = u_cycle[u]
              if (c_next <= uMaxCycle): # if next cycle is less than maxCycle of the unit
                 while (r_next <= cfg.DBParam.MaxRot):        
                    cfg.trsDic[trs_out] = (trs_in,
                                   u, c, r, sp,
                                   'th3',
                                   u, c_next, r_next, sp_next) 
                    trs_out = trs_out + 1
                    r_next = r_next + 1
                 #end while
              #end if
           #end if ttype   
        # end if in PossibleTType 
        
        #---------------------------------------------fourth transition rule 
        #---------------------------------------------------------------fc1
        #----------------------------------------final cut after thinning
        #-------------------------------------- change to species sp = 1        
        #-----------------------------------------------------------c+1, 1
        if cfg.pwDic['fc1'][1]:
           if ttype in ['ina','th1']:            
              sp_next = 1
              c_next = c + 1 
              r_next = 1 
              uMaxCycle = u_cycle[u]
              if (r == cfg.DBParam.MaxRot) and (c_next <= uMaxCycle):
                 cfg.trsDic[trs_out] = (trs_in,
                                u, c, r, sp,
                                'fc1',
                                u, c_next, r_next, sp_next) 
                 trs_out = trs_out + 1
              #-end if---------------
           #end if ttype               
        # end if in PossibleTType
        
        #---------------------------------------------fourth transition rule 
        #---------------------------------------------------------------fc2
        #----------------------------------------final cut after thinning
        #-------------------------------------- change to species sp = 1        
        #-----------------------------------------------------------c+1, 1
        if cfg.pwDic['fc2'][1]:
           if ttype in ['ina','th2']:            
              sp_next = 2
              c_next = c + 1 
              r_next = 1 
              uMaxCycle = u_cycle[u]
              if (r == cfg.DBParam.MaxRot) and (c_next <= uMaxCycle):
                 cfg.trsDic[trs_out] = (trs_in,
                                u, c, r, sp,
                                'fc2',
                                u, c_next, r_next, sp_next) 
                 trs_out = trs_out + 1
              #-end if---------------
           #end if ttype               
        # end if in PossibleTType    
        
        #---------------------------------------------fourth transition rule 
        #---------------------------------------------------------------fc3
        #----------------------------------------final cut after thinning
        #-------------------------------------- change to species sp = 1        
        #-----------------------------------------------------------c+1, 1
        if cfg.pwDic['fc3'][1]:
           if ttype in ['ina','th3']:            
              sp_next = 3
              c_next = c + 1 
              r_next = 1 
              uMaxCycle = u_cycle[u]
              if (r == cfg.DBParam.MaxRot) and (c_next <= uMaxCycle):
                 cfg.trsDic[trs_out] = (trs_in,
                                u, c, r, sp,
                                'fc3',
                                u, c_next, r_next, sp_next) 
                 trs_out = trs_out + 1
              #-end if---------------
           #end if ttype               
        # end if in PossibleTType          

        #-------------------------------------------------- transition rule 
        #---------------------------------------------------------------cl1
        #---------------------------------------------clear cut and renew
        #-------------------------------------- change to species sp = 1
        #--------------------------------------------------c+1, r = 1, 
        if cfg.pwDic['cl1'][1]:
           if ttype in ['ina','cl1','fc1']:              
              sp_next = 1
              c_next = c + 1
              r_next = 1 
              uMaxCycle = u_cycle[u] 
              if (c_next <= uMaxCycle):
                 cfg.trsDic[trs_out] = (trs_in,
                                u, c, r, sp,
                                'cl1',
                                u, c_next, r_next, sp_next) 
                 trs_out = trs_out + 1
              #-end if---------------
           #end if ttype                 
        # end if in PossibleTType
        
        #-------------------------------------------------- transition rule 
        #---------------------------------------------------------------cl2
        #---------------------------------------------clear cut and renew
        #-------------------------------------- change to species sp = 2
        #--------------------------------------------------c+1, r = 1, 
        if cfg.pwDic['cl2'][1]:
           if ttype in ['ina','cl2','fc2']:              
              sp_next = 2
              c_next = c + 1
              r_next = 1 
              uMaxCycle = u_cycle[u] 
              if (c_next <= uMaxCycle):
                 cfg.trsDic[trs_out] = (trs_in,
                                   u, c, r, sp,
                                   'cl2',
                                   u, c_next, r_next, sp_next) 
                 trs_out = trs_out + 1
              #-end if---------------
           #end if ttype                      
        # end if in PossibleTType
        
        #-------------------------------------------------- transition rule 
        #---------------------------------------------------------------cl3
        #---------------------------------------------clear cut and renew
        #-------------------------------------- change to species sp = 3
        #--------------------------------------------------c+1, r = 1, 
        if cfg.pwDic['cl3'][1]: 
           if ttype in ['ina','cl3','fc3']:              
              sp_next = 3
              c_next = c + 1
              r_next = 1 
              uMaxCycle = u_cycle[u] 
              if (c_next <= uMaxCycle):
                 cfg.trsDic[trs_out] = (trs_in,
                                   u, c, r, sp,
                                   'cl3',
                                   u, c_next, r_next, sp_next) 
                 trs_out = trs_out + 1
              #-end if---------------
           #end if ttype
        # end if in PossibleTType        

        trs_in = trs_in + 1
        if trs_in > len(cfg.trsDic):
            break
        #-end if --------    
        
    #end while true

    return MaxCycle
# end trs_gen()---------------------------------------------------------------


#----------------------------------------------------------------------------- 
#------------(2)-alt_gen():
#---------------------------- transitions alternatives within planning horizon
#----------------------------------------------------------------------------- 
def alt_gen():
    
    altt = ()     #age alternatives tuple
    intt = ()     #interventions tuple
    
    tf = len(cfg.trsDic)  #the final transition +
    cfg.LastIntPrev = 0

    for trsi in range(cfg.DBParam.NumUnits+1,tf+1):     ## de 8 a 36
        # for each transition in the transition dictionary
        (trs_prev, u_prev, c_prev, r_prev, sp_prev, ttype, u, c, r, sp) = cfg.trsDic[trsi]
        
        # filter cfg.altList for the same trs_prev
        altl_t = [(ti, pi, ai) for (ti, pi, ai) in cfg.altList if ti == trs_prev]
        altl_sf = []
        #----------------------generate "age alternatives" 
        #----------------------between ccAMin and ccAMin 
        for row_t in altl_t:
            (ti, pi, ai) = row_t
            #-------------------"period = 0" is initial area
            if pi == 0:    
               an = ai + 1
               if an > cfg.pwDic[ttype][7]:  #max age for each type of transition 
                   while an <= cfg.DBParam.MaxAge:
                       pn = an - ai
                       altt = (trsi,pn,an)
                       altl_sf.append(altt) 
                       intt = (ti, pi, ai, ttype, trsi, pn, an)
                       if ti > cfg.LastIntPrev: cfg.LastIntPrev = ti
                       cfg.intList.append(intt)
                       an=an+1
               else:
                   an = max(an,cfg.pwDic[ttype][6]) #minumun age for each type eof transition
                   while an <= cfg.pwDic[ttype][7]:
                       pn = an - ai
                       altt = (trsi,pn,an)
                       altl_sf.append(altt) 
                       intt = (ti, pi, ai, ttype, trsi, pn, an)
                       if ti > cfg.LastIntPrev: cfg.LastIntPrev = ti
                       cfg.intList.append(intt)
                       an=an+1
                      
            #end if(pi == 0):
            # (pi >0)
            else:
                
               # take the previous node to have the ttype_p >>> CycleEnd
               (trs_pp, u_pp, c_pp, r_pp, sp_pp, ttype_p, u_p, c_p, r_p, sp_p) = \
               cfg.trsDic[trs_prev] 
               # ---------------- after cut, age = zero
               # ---------------- think in other alternatives like
               # ---------------- separate cut from renew
               # ---------------- pwDic[ttype][2] = CycleEnd
               
               an =  cfg.pwDic[ttype][6]   #minumun age for each type eof transition
               if cfg.pwDic[ttype_p][3]:   #ReStartAge
                   nextPeriod = an + pi
               else:    
                   nextPeriod = an + pi - ai
                   
               while ( an <= cfg.pwDic[ttype][7] ) and\
                     (   (nextPeriod <= cfg.DBParam.MaxPeriod) or\
                        ((nextPeriod >  cfg.DBParam.MaxPeriod) and (not cfg.pwDic[ttype_p][2]))\
                     ):
                  if cfg.pwDic[ttype_p][3]: 
                     pn = an + pi
                  else:   
                     pn = an + pi - ai
                  altt = (trsi,pn,an)
                  altl_sf.append(altt) 
                  
                  intt = (ti, pi, ai, ttype, trsi, pn, an)
                  if ti > cfg.LastIntPrev: cfg.LastIntPrev = ti 
                  cfg.intList.append(intt)
                  an=an+1
                  
                  nextPeriod = pn
            #end else (pi == 0):    
        #end for row_t in altl_t: 
        altl_sf = set(altl_sf)
        for item in altl_sf:
            cfg.altList.append(item)
 
#end alt_gen()---------------------------------------------------------------- 
#-----------------------------------------------------------------------------

