# Romero-Multicriteria
Multicriteria Optimization fFramework for Industrial Forest Plantation
Version of the Silvana Nobre's PhD thesis 
There are two main programs: 
1 - The one we use to calc and run the model (Plt2_Main.py) 
2 - the one we use to show results (Plt2_ResultsMain.py) 
Both access the database SQLite3 (SilvanaThesis.db) 
Both use Qt to present tables of parameters and results. There are three ".ui" files with qt windows configuration.
The language used is Python.
Library used to create optimization models is Pyomo
The Pyomo Model itself is written on Plt2_SimpleModel.py
To run, three xml file is needed (Plt2_*.xml)
