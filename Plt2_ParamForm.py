# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 13:33:03 2018

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


def UpdateGlobalVariables(qtCreatorFile, MyApp, conn):
    
   #------------------------------------create the Connection to database   
   dbProject = QtSql.QSqlDatabase()
   dbProject = QtSql.QSqlDatabase.addDatabase('QSQLITE')
   dbProject.setDatabaseName(cfg.gvDic['DatabaseFile'])
   if dbProject.isValid(): print("SQL db instance OK")
   else: 
      print("SQL db instance error = "+ dbProject.lastError().text())
      
   if not dbProject.open(): print(dbProject.lastError().text())
   else: print("Database connected")

   gpClass = uic.loadUiType(qtCreatorFile)[0]  # Load the UI
   pwFieldList = ['Transition Type','Description','Possible','Cycle End','Restart Age','Plantation','Production','Min Age to Cut','Max Age to Cut']

   #---------------------------------------------------subClass of a TableModel
   class pwTableModel(QtSql.QSqlTableModel):
      def __init__(self, parent=None, *args):
        super(pwTableModel, self).__init__()
 
        self.setTable('TransitionType') 
        Erro = self.lastError()
        
        print("erro =",str(Erro.text()))
        print("erro =",str(Erro.databaseText()))        
        
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.setSort(0, 0)
                    
        if self.select(): print("select OK") 
        else: print("select error")
        
        for i in range(0,len(pwFieldList)):
          self.setHeaderData(i, QtCore.Qt.Horizontal, pwFieldList[i])
    
      def flags(self, index):
        itemFlags = super(pwTableModel, self).flags(index)
        itemFlags = itemFlags | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        return itemFlags
    
      def data(self, item, role):
        val = QtSql.QSqlTableModel.data(self, item, role)
        row = item.row()
        column = item.column()
        
        if role == QtCore.Qt.CheckStateRole and column == 2:
            if str(item.data()) == 'True':
               return QtCore.QVariant(QtCore.Qt.Checked)
            else:
               return QtCore.QVariant(QtCore.Qt.UnChecked)   
           
        if role == Qt.DisplayRole:
            if column in (7,8):
               try:
                  return '{:{}{}{}}'.format(val, '>', '-', 10)
               except ValueError:
                  pass
        if role == Qt.EditRole:
            if column in (7,8):
               try:
                  return val
               except ValueError:
                  pass
        if role == QtCore.Qt.TextAlignmentRole:
            if column in (7,8):
               return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter    
        return val   
   #end class pwTableModel(QtSql.QSqlTableModel)        
    
   class CheckBoxDelegate(QtWidgets.QStyledItemDelegate):
      """
      A delegate that places a fully functioning QCheckBox in every
      cell of the column to which it's applied
      """
    
      def __init__(self, parent):
          QtWidgets.QItemDelegate.__init__(self, parent)


      def createEditor(self, parent, option, index):
          #Important, otherwise an editor is created if the user clicks in this cell.
          #** Need to hook up a signal to the model
          return None


      def paint(self, painter, option, index):
          #Paint a checkbox without the label.

          if   index.data() in ('OK', 'Ok', 'ok', 'True' , 'true' , 'Yes', 'yes','1'): 
               checked = bool(1)
          elif index.data() in ('False', 'false', 'No' , 'no' ,'0'):
               checked = bool(0)
          else: checked = bool(0)
        
          check_box_style_option        = QtWidgets.QStyleOptionButton()
          check_box_style_option.state |= QtWidgets.QStyle.State_Enabled
          check_box_style_option.rect = self.getCheckBoxRect(option)
        
          if checked: check_box_style_option.state |= QtWidgets.QStyle.State_On
          else:       check_box_style_option.state |= QtWidgets.QStyle.State_Off

          QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_CheckBox, check_box_style_option, painter)


      def editorEvent(self, event, model, option, index):

        if   index.data() in ('OK', 'Ok', 'ok', 'True' , 'true' , 'Yes', 'yes','1'): 
             checked = bool(1)
        elif index.data() in ('False', 'false', 'No' , 'no' ,'0'):
             checked = bool(0)
        else: checked = bool(0)        
        
        if event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick) :   
           if checked: x = 'False'
           else: x = 'True'
           model.setData(index, x)
           return True
      
        return False 
       
        
      def getCheckBoxRect(self, option):
          check_box_style_option = QtWidgets.QStyleOptionButton()
          check_box_rect = QtWidgets.QApplication.style().subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
          check_box_point = QtCore.QPoint (option.rect.x() +
                            option.rect.width() / 2 -
                            check_box_rect.width() / 2,
                            option.rect.y() +
                            option.rect.height() / 2 -
                            check_box_rect.height() / 2)
          return QtCore.QRect(check_box_point, check_box_rect.size())
   #end class CheckBoxDelegate(QtWidgets.QStyledItemDelegate)

    
   class MyTableModel(QtSql.QSqlRelationalTableModel):
      def __init__(self, parent=None, *args):
        super(MyTableModel, self).__init__()
        self.TableName      = ''
        self.FieldList      = []
        self.IntegerColumns = []
        self.FloatColumns   = []
        
      def ConfigTable(self,TableName, FieldList, IntegerColumns, FloatColumns):
        self.TableName      = TableName
        self.FieldList      = FieldList
        self.IntegerColumns = IntegerColumns
        self.FloatColumns   = FloatColumns

        self.setTable(self.TableName) 
        Erro = self.lastError()
        
        if len(Erro.text()) > 1:
           print("erro =",str(Erro.text()))
           print("erro =",str(Erro.databaseText()))        
        
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.setSort(0, 0)
                    
        if self.select(): print("SQL Select from a table OK") 
        else: print("SQL Select from a table with error")
        
        for i in range(0,len(FieldList)):
          self.setHeaderData(i, QtCore.Qt.Horizontal, FieldList[i])

        
      def flags(self, index):
        itemFlags = super(MyTableModel, self).flags(index)
        itemFlags = itemFlags | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        return itemFlags
    
      def data(self, item, role):
        val    = QtSql.QSqlTableModel.data(self, item, role)
        column = item.column()
        self.NumberColumns =  self.IntegerColumns + self.FloatColumns
        if role == Qt.DisplayRole:
            if column in self.IntegerColumns:
               try:               return '{:{}{}{}}'.format(val, '>', '-', 10)
               except ValueError: pass
            if column in self.FloatColumns:
               try:               return '{:,.3f}'.format(val)
               except ValueError: pass
        if role == Qt.EditRole:
            if column in self.NumberColumns:
               try:               return val
               except ValueError: pass
        if role == QtCore.Qt.TextAlignmentRole:
            if column in self.NumberColumns:
               return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        return val   
   
    
   class gParamClass(QMainWindow, gpClass):
       
      def __init__(self, parent=None):
         QMainWindow.__init__(self, parent)
         gpClass.__init__(self)
         # General Parameters
         self.setupUi(self)
         
         self.Next0Button.clicked.connect(self.Next0Button_clicked)
         self.Next1Button.clicked.connect(self.Next1Button_clicked)
         self.Next2Button.clicked.connect(self.Next2Button_clicked)
         self.RunButton.clicked.connect(self.close)   
         self.ParametersTab.currentChanged.connect(self._tab_changed)
         self.ParamPage = 0

         self.dbFileButton.clicked.connect(self.dbFileButton_clicked)
         self.wDirButton.clicked.connect(self.wDirButton_clicked)
         self.dbFileEdit.setText(cfg.gvDic['DatabaseFile'])
         self.wDirEdit.setText(cfg.gvDic['WorkingDirectory'])
         self.simEdit.setText(cfg.gvDic['SimulationTitle'])
         self.simDescEdit.setText(cfg.gvDic['SimulationDesc'])
         self.solverEdit.setText(cfg.gvDic['MySolver'])
         self.LastIgorLabel.text = str(cfg.ParamIgor)
         
           
         if   cfg.gvDic['RunType'] == 'PayOffMatrix':
            self.poMatrixRButton.setChecked(True)
         elif cfg.gvDic['RunType'] == 'ParetoFrontier':
            self.pFrontierRButton.setChecked(True)
         elif cfg.gvDic['RunType'] == 'MonteCarlo':
            self.mCarloRButton.setChecked(True) 
         elif cfg.gvDic['RunType'] == 'InitialArea':
            self.IniAreaRButton.setChecked(True)   

         # Optimization Parameters
         #---------------------------------------------------Fill Criteria list
         NotInSelectionList = [item for item in cfg.ObjectiveDic.keys() if item not in cfg.ObjSelectionL ] 
         for item1 in NotInSelectionList:
             self.CriteriaList.addItem(item1)
         for item2 in cfg.ObjSelectionL:
             self.OptCriteriaList.addItem(item2)  
         #-------------------------------------------------Set Values and rates
         self.ProdPcPrevMinSpin.setValue(cfg.OptParam.ProdPcPrevMin)
         self.ProdPcPrevMaxSpin.setValue(cfg.OptParam.ProdPcPrevMax)
         
         self.GenMatMinSpin.setValue(cfg.OptParam.GenMatMin)
         self.GenMatMaxSpin.setValue(cfg.OptParam.GenMatMax)   
         
         self.discRateSpin.setValue(cfg.OptParam.discRate)
         self.IgorValueSpin.setValue(cfg.OptParam.IgorValue)
         self.goalRateSpin.setValue(cfg.OptParam.goalRate) 
         self.mcIterationsSpin.setValue(int(cfg.OptParam.mcIterations))          
         self.Period2MaxSpin.setValue(cfg.OptParam.Period2Max)
         self.Period2FlowSpin.setValue(cfg.OptParam.Period2Flow)
         
         self.rgControlPeriodSpin.setValue(cfg.OptParam.rgControlPeriod)
         self.rgControlPcPrevSpin.setValue(cfg.OptParam.rgControlPcPrev)
         self.rgLastAgeClassSpin.setValue(cfg.OptParam.rgLastAgeClass)
         #----------------------------------------------Set Optional contraints 
         if cfg.OptParam.conNDY            == 'yes': self.conNDYBox.setChecked(True) 
         else:                                       self.conNDYBox.setChecked(False) 
         if cfg.OptParam.conMktProd        == 'yes': self.conMktProdBox.setChecked(True) 
         else:                                       self.conMktProdBox.setChecked(False)
         if cfg.OptParam.conMillPrd        == 'yes': self.conMillPrdBox.setChecked(True) 
         else:                                       self.conMillPrdBox.setChecked(False)
         if cfg.OptParam.conRangeProd      == 'yes': self.conRangeProdBox.setChecked(True) 
         else:                                       self.conRangeProdBox.setChecked(False)
         if cfg.OptParam.conGenMatSecurity == 'yes': self.conGenMatSecurityBox.setChecked(True) 
         else:                                       self.conGenMatSecurityBox.setChecked(False)      
         if cfg.OptParam.conIgor           == 'yes': self.conIgorBox.setChecked(True) 
         else:                                       self.conIgorBox.setChecked(False)           
         #----------------------------------------------Set Regulation Variable
         if   cfg.OptParam.Regulation == 'Area':    self.AreaRButton.setChecked(True)
         elif cfg.OptParam.Regulation == 'TotProd': self.TotProdRButton.setChecked(True) 
         elif cfg.OptParam.Regulation == 'Prod1':   self.Prod1RButton.setChecked(True) 

         #-----------------------------------------------------------------------------
         # prescription Writer Parameters
         #-----------------------------------------------------------------------------
         self.tTypeModel = pwTableModel()
         self.TTypeTableView.setModel(self.tTypeModel) 
         self.TTypeTableView.setWindowTitle('Transition Types')
         self.TTypeTableView.setSortingEnabled(True)
         for i in [2,3,4,5,6]:
             self.TTypeTableView.setItemDelegateForColumn(i,CheckBoxDelegate(self))
         self.TTypeTableView.show()

         #-----------------------------------------------------------------------------
         # General Funcion to link a TableModel to a TableView and show them
         #-----------------------------------------------------------------------------
         def ModelTableViewLink (MyTableView, MyTableName):
             MyModel = MyTableModel()
             MyModel.ConfigTable(MyTableName,cfgDB.DicTable[MyTableName][0],
                                             cfgDB.DicTable[MyTableName][1],
                                             cfgDB.DicTable[MyTableName][2])
             for row in cfgDB.DicJoin[MyTableName]:
                 (NumColumn,(SqlTable, SqlKey, SqlDesc)) = row
                 MyModel.setRelation(NumColumn,QtSql.QSqlRelation(SqlTable, SqlKey, SqlDesc))

             MyTableView.setModel(MyModel) 
             MyTableView.setSortingEnabled(True)
             if len(cfgDB.DicJoin[MyTableName])>0:
                MyTableView.setItemDelegate(QtSql.QSqlRelationalDelegate(MyTableView))
             MyTableView.show()   
             
         ModelTableViewLink(self.VariableTableView,     'Variable')
         ModelTableViewLink(self.RegionTableView,       'Region')
         ModelTableViewLink(self.MarketTableView,       'Market')         
         ModelTableViewLink(self.SpeciesTableView,      'Species')
         ModelTableViewLink(self.ProductTableView,      'Product')
         ModelTableViewLink(self.IniAreaTableView,      'InitialArea')
         ModelTableViewLink(self.ProductivityTableView, 'Production')
         ModelTableViewLink(self.MktDemandTableView,    'MarketDemand')
         ModelTableViewLink(self.TimberPriceTableView,  'Price')
         ModelTableViewLink(self.CarbonPriceTableView,  'Period')
         ModelTableViewLink(self.HarvestCstTableView,   'HarvCosts')
         ModelTableViewLink(self.SilvCstTableView,      'SilvCosts')

        
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
         
            
      def _tab_changed(self, _index):
         if   self.ParamPage == 0:
            #-----------------------------------------------------save new global variables
            #-------------------------------------------------into the same inital xml file
            # general parameters
            cfg.gvDic['DatabaseFile']     = str(self.dbFileEdit.text())
            cfg.gvDic['WorkingDirectory'] = str(self.wDirEdit.text())
            cfg.gvDic['SimulationTitle']  = str(self.simEdit.text())
            cfg.gvDic['SimulationDesc'] = str(self.simDescEdit.text())
            cfg.gvDic['MySolver']         = str(self.solverEdit.text())
   
            if self.poMatrixRButton.isChecked():
               cfg.gvDic['RunType'] = 'PayOffMatrix'
            if self.pFrontierRButton.isChecked():
               cfg.gvDic['RunType'] = 'ParetoFrontier'
            if self.mCarloRButton.isChecked():
               cfg.gvDic['RunType'] = 'MonteCarlo'
            if self.IniAreaRButton.isChecked():
               cfg.gvDic['RunType'] = 'InitialArea'     
            SaveGlobalVariables('Plt2_GlobalVar.xml') 
            self.ParamPage = _index
   
         elif self.ParamPage == 1:
            #-------------------------------------------save updated optmization parameters
            #-------------------------------------------------into the same inital xml file
            #----------------------------------------------------Save Criteria Selection
            cfg.ObjSelectionL = []
            for row in range(self.OptCriteriaList.count()): 
              cfg.ObjSelectionL.append(self.OptCriteriaList.item(row).text())
            #------------------------------------------------------Save Values and rates  
            cfg.OptParam.ProdPcPrevMin   = self.ProdPcPrevMinSpin.value()
            cfg.OptParam.ProdPcPrevMax   = self.ProdPcPrevMaxSpin.value()
            cfg.OptParam.GenMatMin       = self.GenMatMinSpin.value()
            cfg.OptParam.GenMatMax       = self.GenMatMaxSpin.value()
            cfg.OptParam.discRate        = self.discRateSpin.value()
            cfg.OptParam.IgorValue       = self.IgorValueSpin.value()            
            cfg.OptParam.goalRate        = self.goalRateSpin.value()
            cfg.OptParam.mcIterations    = int(self.mcIterationsSpin.value())  
            cfg.OptParam.Period2Max      = self.Period2MaxSpin.value()
            cfg.OptParam.Period2Flow     = self.Period2FlowSpin.value()   
            cfg.OptParam.rgControlPeriod = self.rgControlPeriodSpin.value()
            cfg.OptParam.rgControlPcPrev = self.rgControlPcPrevSpin.value()
            cfg.OptParam.rgLastAgeClass  = self.rgLastAgeClassSpin.value()
            #--------------------------------------------------Save Optional Constraints
            if self.conNDYBox.isChecked():            cfg.OptParam.conNDY           = 'yes'
            else:                                     cfg.OptParam.conNDY            = 'no'  
            if self.conMktProdBox.isChecked():        cfg.OptParam.conMktProd        = 'yes'
            else:                                     cfg.OptParam.conMktProd        = 'no' 
            if self.conMillPrdBox.isChecked():        cfg.OptParam.conMillPrd        = 'yes'
            else:                                     cfg.OptParam.conMillPrd        = 'no' 
            if self.conRangeProdBox.isChecked():      cfg.OptParam.conRangeProd      = 'yes'
            else:                                     cfg.OptParam.conRangeProd      = 'no' 
            if self.conGenMatSecurityBox.isChecked(): cfg.OptParam.conGenMatSecurity = 'yes'
            else:                                     cfg.OptParam.conGenMatSecurity = 'no'   
            if self.conIgorBox.isChecked():           cfg.OptParam.conIgor           = 'yes'
            else:                                     cfg.OptParam.conIgor           = 'no'   
            
            #---------------------------------------------------Save Regulation Variable
            if self.AreaRButton.isChecked() == True:
               cfg.OptParam.Regulation = 'Area'
            if self.TotProdRButton.isChecked() == True:   
               cfg.OptParam.Regulation = 'TotProd'
            if self.Prod1RButton.isChecked() == True:   
               cfg.OptParam.Regulation = 'Prod1'


            NumCriteria = self.OptCriteriaList.count() 
            CanLeave = False
            RunTypeString = str(cfg.gvDic['RunType'])
            if RunTypeString in ('PayOffMatrix','GoalProgramming'):
               if (NumCriteria >= 1): CanLeave = True 
               else: InfoText = 'To run PayOff or GoalProgramming we need at least one criterion' 
            else: 
               if RunTypeString == 'ParetoFrontier':
                  if (NumCriteria >= 2): CanLeave = True 
                  else: InfoText = 'To run a Pareto Frontier Procedure we need at least 2 criteria' 
               else:   
                  if RunTypeString == 'MonteCarlo':
                     if (NumCriteria >= 1): CanLeave = True              
                     else: InfoText = 'To run a Monte Carlo Procudure we need at least one criterion'  
            if CanLeave:
               SaveOptVariables('Plt2_OptVar.xml')  
               InitCrtSelectionL()
               self.ParamPage = _index 
            else:
              msg = QMessageBox()
              MsgText = "Error in Criteria selection"
              msg.setStandardButtons(QMessageBox.Ok)
              buttonReply = QMessageBox.critical(self, MsgText, InfoText, QMessageBox.Ok, QMessageBox.Ok)
              self.ParametersTab.setCurrentIndex(1)
              pass
          
         elif self.ParamPage == 2:
            NumRows = self.tTypeModel.rowCount()
            tTypeKey = ''
            tTypeRow = ()
            for i in range(NumRows):
                tTypeKey =  self.tTypeModel.record(i).value("ttype")
                tTypeRow = (self.tTypeModel.record(i).value("trsDescription"),
                            StrToBoolean(self.tTypeModel.record(i).value("Possible")),
                            StrToBoolean(self.tTypeModel.record(i).value("CycleEnd")),
                            StrToBoolean(self.tTypeModel.record(i).value("ReStartAge")),
                            StrToBoolean(self.tTypeModel.record(i).value("Plantation")),
                            StrToBoolean(self.tTypeModel.record(i).value("Production")),
                            self.tTypeModel.record(i).value("ccAMin"),
                            self.tTypeModel.record(i).value("ccAMax"))
                cfg.pwDic[tTypeKey] = tTypeRow
            self.ParamPage = _index     
            
         # end of ifs and elses of tabs
      # end of "def __init__(self, parent=None)"        

      def Next0Button_clicked(self): 
         self.ParametersTab.setCurrentIndex(1)
 
      def Next1Button_clicked(self): 
         self.ParametersTab.setCurrentIndex(2)

      def Next2Button_clicked(self): 
         self.ParametersTab.setCurrentIndex(3)  

      def keyPressEvent(self, e):
         if e.key() == QtCore.Qt.Key_Escape:
            self.close() 
            
      def closeEvent(self, event):
        reply = QMessageBox()
        reply = QMessageBox.question(
            self, "Message",
            "Are you sure you want to finish Parameter definitions and run the model ? ",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            dbProject.commit()
            dbProject.close()
            cfg.Calculate = True            
            event.accept()
        elif reply == QMessageBox.Cancel:
            dbProject.commit()
            dbProject.close()
            cfg.Calculate = False
            event.accept()    
        else:
            pass   
      
   def StrToBoolean (xStr):
       if   xStr in ('OK', 'Ok', 'ok', 
                     'True' , 'true' , 'Yes', 'yes','1'): stb = True 
       elif xStr in ('False', 'false', 'No' , 'no' ,'0'): stb = False
       else:                                              stb = None
       return stb
    
   # open the window       
   gpWindow = gParamClass(None)
   gpWindow.show()
   MyApp.exec_()

   #Create New Simulation Record
   with conn: 
      str_sql = "SELECT seq FROM SQLITE_SEQUENCE where name = 'Simulation'"
      IdSimCursor = conn.cursor()
      IdSimCursor.execute(str_sql)
      IdSimList = IdSimCursor.fetchone()
      idSimulation = IdSimList[0] + 1 
      cfg.gvDic['idSimulation'] = idSimulation
      IdSimCursor.close()
      cfg.gvDic['SimulationTitle'] = str(idSimulation)+"-"+str(cfg.gvDic['SimulationTitle'])
      cfg.gvDic['idSimulation']    = idSimulation
       
      str_sql = "insert into Simulation (SimName, SimDescription, SimDate, SimIterations) "\
               +"values ("\
               + "'"+str(cfg.gvDic['SimulationTitle'])+"' , "\
               + "'"+str(cfg.gvDic['SimulationDesc']) +"' , "\
               + " datetime('now') , "\
               + str(cfg.OptParam.mcIterations) + " )"
      cursorSim = conn.cursor()         
      cursorSim.execute(str_sql)
      cursorSim.close()
   conn.commit()

   
#end def UpdateGlobalVariables(qtCreatorFile):   

