# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 08:14:20 2018

@author: SilvanaNobre
"""

from PyQt5 import QtSql, QtCore, QtGui, uic, Qt, QtWidgets

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QLabel
from PyQt5.QtWidgets import QGraphicsView, QWidget, QLineEdit,QTableWidget, QTableWidgetItem, QGraphicsScene
from PyQt5.QtGui import * #QIcon 
from PyQt5.QtCore import * #Qt, pyqtSlot
from operator import itemgetter, attrgetter, methodcaller

import sys 
import os
import Plt2_Lib
import cfg
import cfgDB
import math
from Plt2_Lib import *

import sqlite3
import pandas 
import numpy as np

import plotly
import plotly.plotly as py
import plotly.offline as offline
import plotly.graph_objs as go
from plotly.offline import plot

def SelectSimulaton(qtCreatorFile,MyApp):
   #------------------------------------create the Connection to database   
   ssClass = uic.loadUiType(qtCreatorFile)[0]  # Load the UI  
   
   class SelSimClass(QMainWindow, ssClass):
      def __init__(self, parent=None):
         QMainWindow.__init__(self, parent)
         ssClass.__init__(self)
         self.setupUi(self)
         self.OKButton.clicked.connect(self.close)
         self.SimulationCombo.currentIndexChanged.connect(self.ComboChanged)

         self.dbFileButton.clicked.connect(self.dbFileButton_clicked)
         self.wDirButton.clicked.connect(self.wDirButton_clicked)
         self.dbFileEdit.setText(cfg.gvDic['DatabaseFile'])
         self.wDirEdit.setText(cfg.gvDic['WorkingDirectory'])
         
         self.SimModel = QtSql.QSqlTableModel(self)
         self.SimModel.setTable("Simulation")
         self.SimModel.select()         
         self.SimulationCombo.setModel(self.SimModel)
         self.SimulationCombo.setModelColumn(self.SimModel.fieldIndex("SimName"))
         self.SimulationCombo.setCurrentText(cfg.gvDic['SimName'])
         
         self.idSimulationLabel.setText(str(cfg.gvDic['idSimulation']))
         
      def ComboChanged(self,i):
          self.idSimulationLabel.setText(str(self.SimModel.record(i).field(0).value()))

      def dbFileButton_clicked(self):
           dbDialog = QFileDialog()
           dbDialog.setFileMode(QFileDialog.ExistingFile)
           options = dbDialog.Options()
           dbCurrentFile = str(self.dbFileEdit.text())
                
           fileName, _ = QFileDialog.getOpenFileName(self,"Choose Database File", 
                                                          dbCurrentFile,
                                                          "db files (*.db)", 
                                                          options=options)
           if fileName:
               self.dbFileEdit.setText(fileName)
            
      def wDirButton_clicked(self):
         pfDialog = QFileDialog()
         pfDialog.setFileMode(QFileDialog.DirectoryOnly)
         wCurrentDir = str(self.wDirEdit.text())

         wDirName = QFileDialog.getExistingDirectory(self, "Working Directory", 
                                                            wCurrentDir , 
                                                            QFileDialog.ShowDirsOnly)
         if wDirName != "":
            self.wDirEdit.setText(wDirName)

      def closeEvent(self, event):   
          cfg.gvDic['DatabaseFile']     = str(self.dbFileEdit.text())
          cfg.gvDic['WorkingDirectory'] = str(self.wDirEdit.text())
          cfg.gvDic['idSimulation'] = int(self.idSimulationLabel.text())
          event.accept()
          #atualizar o idSimulation

   ssWindow = SelSimClass(None)
   ssWindow.show()
   MyApp.exec_()
   
   SaveGlobalVariables('Plt2_GlobalVar.xml')
    
  
   
# end SelectSimulation    

def ShowResults(qtCreatorFile,MyApp,conn):
    
   
   srClass = uic.loadUiType(qtCreatorFile)[0]  # Load the UI
   #-------------------------------------------------------------------------------------
   #Trade Off Model
   #-------------------------------------------------------------------------------------
   TOFieldList = ['IdResult', 'Termination','Monte Carlo Iteration', 'RunType', 'PlotPoint', 'Objective','Obj Value', \
                  'Total Area', 'Total Production', 'Total Prod Period P', 'Total Stock', 'Total Revenue', \
                  'Total Cost' , 'Total NPV' , 'Total Mill Prd', 'Total Igor', 'Total Deviation from Goals']
   
   class TOQueryModel(QtSql.QSqlQueryModel):
      def __init__(self, parent=None, *args):
        super(TOQueryModel, self).__init__()
        SQLString = "select IdResult, Termination, mcIteration, RunType, PlotPoint, Objective, ObjValue, \
            xTotalArea, xTotalProd, xTotalPrdPP, xTotalStk, xTotalRev, \
            xTotalCst, xTotalNPV, xTotalMill1, xTotalIgor, xTotalDev \
            from v_Tradeoffs where IdSimulation = "
            
        SQLString2 = str(cfg.gvDic['idSimulation']) + " order by idResult"
        SQLString = SQLString + SQLString2 
        self.setQuery(SQLString)
        
        Erro = self.lastError()
        if Erro.text() not in ['',' ']:
           print("erro TOQueryModel =",str(Erro.text()))
        
        lenList = len(TOFieldList)
        for i in range(0,lenList):
            self.setHeaderData(i, QtCore.Qt.Horizontal, TOFieldList[i])

      def flags(self, index):
        itemFlags = super(TOQueryModel, self).flags(index)
        itemFlags = itemFlags | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        return itemFlags
    
      def data(self, item, role):
        val    = QtSql.QSqlQueryModel.data(self, item, role)
        column = item.column()
        IntegerColumns = [2,4]
        FloatColumns = [6,7,8,9,10,11,12,13,14,15]
        NumberColumns =  IntegerColumns + FloatColumns
        if role == Qt.DisplayRole:
            if column in IntegerColumns:
               try:               return '{:{}{}{}}'.format(val, '>', '-', 10)
               except ValueError: pass
            if column in FloatColumns:
               try:               return '{:,.3f}'.format(val)
               except ValueError: pass
        if role == Qt.EditRole:
            if column in NumberColumns:
               try:               return val
               except ValueError: pass
        if role == QtCore.Qt.TextAlignmentRole:
            if column in NumberColumns:
               return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        return val 
            
   TradeOffModel = TOQueryModel() 
   
   #-------------------------------------------------------------------------------------
   # Result Model
   #-------------------------------------------------------------------------------------         
   RsFieldList = ['idResult', 'ResDescription', 'Objective', 'ObjValue', 'Variable', 'VarIndex', 'Value']
   class RsQueryModel(QtSql.QSqlQueryModel):
      def __init__(self, parent=None, *args):
        super(RsQueryModel, self).__init__()
        SQLString = "select idResult, ResDescription, Objective, ObjValue, Variable, VarIndex, Value \
                       from v_Results where Value > 0 and idSimulation = "
            
        SQLString2 = str(cfg.gvDic['idSimulation']) + " order by idResult, Variable, VarIndex"
        SQLString = SQLString + SQLString2 
        self.setQuery(SQLString) 
        
        Erro = self.lastError()
        if Erro.text() not in ['',' ']:
           print("erro RsQueryModel =",str(Erro.text()))
        
        lenList = len(RsFieldList)
        for i in range(0,lenList):
            self.setHeaderData(i, QtCore.Qt.Horizontal, RsFieldList[i])  
            
      def flags(self, index):
        itemFlags = super(RsQueryModel, self).flags(index)
        itemFlags = itemFlags | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        return itemFlags
    
      def data(self, item, role):
        val    = QtSql.QSqlQueryModel.data(self, item, role)
        column = item.column()
        FloatColumns = [3,6] 
        NumberColumns =  FloatColumns
        if role == Qt.DisplayRole:
           if column in FloatColumns:
               try:               return '{:,.3f}'.format(val)
               except ValueError: pass
        if role == Qt.EditRole:
            if column in NumberColumns:
               try:               return val
               except ValueError: pass
        if role == QtCore.Qt.TextAlignmentRole:
            if column in NumberColumns:
               return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        return val 
            
   ResultsModel = RsQueryModel()

   
   class ResultsClass(QMainWindow, srClass):
      def __init__(self, parent=None):
           QMainWindow.__init__(self, parent)
           srClass.__init__(self)
           self.setupUi(self)
           
           self.ResultViewTable.itemSelectionChanged.connect(self.ItemSelChanged)
           
           SolverTextFile=open('Plt2_SolverResults.txt').read()
           self.SolverText.setPlainText(SolverTextFile)

           LogTextFile=open('Plt2_LogList.txt').read()
           self.LogText.setPlainText(LogTextFile)
           
           #--- prepare POMatrixView
           self.POMatrixView.setModel(TradeOffModel) 
           self.POMatrixView.setWindowTitle('TradeOff Matrix')
           self.POMatrixView.show()

           #-------------------------------------------------------------------    
           #--- prepare POMatrixCalcTable    
           #-------------------------------------------------------------------
           lenMatrix = len(cfg.MatrixTableDic)
           if lenMatrix == 0: ReadMatrixFromDB()
           
           Rows = max(cfg.MatrixTableDic.keys(), key=itemgetter(0))[0] + 1
           Cols = max(cfg.MatrixTableDic.keys(), key=itemgetter(1))[1] + 1
           print("OPMatrix Rows ="+str(Rows))
           print("OPMatrix Cols ="+str(Cols))           
           self.POMatrixCalcTable.setRowCount(Rows)
           self.POMatrixCalcTable.setColumnCount(Cols)
           
           LabelList = [] 
           for coli in range(0,Cols): LabelList.append(cfg.MatrixTableDic[-1,coli])
           self.POMatrixCalcTable.setHorizontalHeaderLabels(LabelList)
           self.POMatrixCalcTable.resizeColumnsToContents()

           for coli in range(0, Cols):
             for rowi in range(0, Rows):
               item = QTableWidgetItem()
               item.setData(Qt.EditRole,cfg.MatrixTableDic[rowi,coli])
               if coli != 1: item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
               self.POMatrixCalcTable.setItem(rowi,coli, item)
               #self.POMatrixCalcTable.setItem(rowi,coli, \
               #     QTableWidgetItem(str(cfg.MatrixTableDic[rowi,coli])))


           #-------------------------------------------------------------------    
           #--- prepare ResultViewTable    
           #-------------------------------------------------------------------
           MRFieldList = ['IdResult', 'mcIteration', 'Objective', 'ObjValue',
            'xTotalArea', 'xTotalProd', 'xTotalPrdPP', 'xTotalStk', 'xTotalRev',
            'xTotalCst', 'xTotalNPV', 'xTotalMill1', 'xTotalIgor', 'xTotalDev']
           
           SQLString = "select IdResult, mcIteration, Objective, ObjValue, \
            xTotalArea, xTotalProd, xTotalPrdPP, xTotalStk, xTotalRev, \
            xTotalCst, xTotalNPV, xTotalMill1, xTotalIgor, xTotalDev \
            from v_Tradeoffs where Termination = 'optimal' and idSimulation = "
           SQLString2 = str(cfg.gvDic['idSimulation']) + " order by idResult"
           SQLString = SQLString + SQLString2 
           PrdResQuery = QtSql.QSqlQuery()
           PrdResQuery.exec(SQLString)
           
           Erro = PrdResQuery.lastError()
           if Erro.text() not in ['',' ']:
              print("erro ResultViewTable=",str(Erro.text()))
           
           Cols = len(MRFieldList)
           Rows= 0
           #SQLite does not have this feature
           Rows = PrdResQuery.size()
           if Rows == -1:
               PrdResQuery.last()
               Rows = PrdResQuery.at() + 1
               PrdResQuery.exec(SQLString)
               
           self.ResultViewTable.setRowCount(Rows)
           self.ResultViewTable.setColumnCount(Cols)           
           self.ResultViewTable.setHorizontalHeaderLabels(MRFieldList)
           self.ResultViewTable.resizeColumnsToContents()           
           # --- put query data into table 
           rowi = 0
           myData = QtCore.QVariant()
           while (PrdResQuery.next()):
             for coli in range(0, Cols):  
               item = QTableWidgetItem()
               myData = PrdResQuery.value(MRFieldList[coli])
               if coli in (0,1):
                  item.setData(Qt.EditRole,myData) 
                  item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
               elif coli > 2:
                  try: 
                    myDataStr = "{:,.3f}".format(float(myData)) 
                  except:  
                    myDataStr = str(myData) 
                  item.setData(Qt.EditRole,myDataStr) 
                  item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
               else:  
                  item.setData(Qt.EditRole,myData) 
               self.ResultViewTable.setItem(rowi,coli, item)
             rowi = rowi + 1

           #-------------------------------------------------------------------    
           #--- prepare PrdGraphView    
           #-------------------------------------------------------------------

           self.PrdScene=QGraphicsScene()
           self.PrdGraphView.setScene(self.PrdScene)


           #-------------------------------------------------------------------
           #--- prepare Text Results
           #-------------------------------------------------------------------
           ModelTextFile=open('Plt2_TextModel.txt').read()
           self.ModelText.setPlainText(ModelTextFile)
           
           LPModelTextFile=open('Plt2_LpModel.lp').read()
           self.LPModelText.setPlainText(LPModelTextFile)     
           
           ParamTextFile=open('Plt2_Parameters.txt').read()
           self.ParamText.setPlainText(ParamTextFile)            
           
           TrsTextFile=open('Plt2_Transitions.txt').read()
           self.TrsText.setPlainText(TrsTextFile)
           
           IntTextFile=open('Plt2_Interventions.txt').read()
           self.IntText.setPlainText(IntTextFile)
           
           cIntTextFile=open('Plt2_CompleteInt.txt').read()
           self.cIntText.setPlainText(cIntTextFile)
           
           FinalTextFile=open('Plt2_FinalNodes.txt').read()
           self.FinalText.setPlainText(FinalTextFile)
           
           self.ResultsView.setModel(ResultsModel) 
           self.ResultsView.setWindowTitle('TradeOff Matrix')
           self.ResultsView.show()   

      def ItemSelChanged(self): 
          #descobrir onde está
          TableRow = self.ResultViewTable.currentRow()
          idResultItem  = self.ResultViewTable.item(TableRow,0)
          ObjectiveItem = self.ResultViewTable.item(TableRow,2)
          print("ItemSelChanged1")
          idResult = idResultItem.text()
          Criterion = ObjectiveItem.text() 
          SqlGraph = "select period,matgen,production from v_ProductionMatgen where period >= '01' and idResult =" + \
                     idResult + " order by 1,2" 
          dfGraph = pandas.read_sql_query(SqlGraph, conn)
          
          graphTitle = 'Regularity Model - '+ Criterion +' (' +idResult +')'
          
          fig = {'data' : [{'x':    dfGraph[dfGraph['matgen']==mg]['period'], 
                            'y':    dfGraph[dfGraph['matgen']==mg]['production'],
                            'name': mg,
                            'mode': 'lines'
                            } for mg in ['1','2','3'] 
                          ], 
                'layout': {'xaxis': {'title': 'Period (years)'},
                           'yaxis': {'title': 'Production (m3)'},
                           'title': graphTitle,
                           'subtitle': Criterion,
                          } 
                }
          #offline.plot(fig, filename='regularity.html', 
                       #image='jpeg', 
                       #image_filename = 'regularity' )
                       
          ImageFileName = "regularity"+ idResult +".jpeg"
          py.image.save_as(fig, ImageFileName) 
          #show into the iPython window
          #py.image.ishow(fig)
          print("ItemSelChanged2")
          PrdImage = QtGui.QPixmap(ImageFileName)

          self.PrdScene.clear()
          self.PrdScene.addPixmap(PrdImage)
          self.PrdGraphView.fitInView(self.PrdScene.sceneRect(), Qt.KeepAspectRatio)
          self.PrdScene.update()
          self.PrdGraphView.show()
          #os.remove(ImageFileName)
          
      #def closeEvent(self, event):  
      
   srWindow = ResultsClass(None)
   srWindow.show()
   MyApp.exec_()

   
# end: def showResults
   
