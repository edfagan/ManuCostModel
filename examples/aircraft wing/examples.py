# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 16:10:42 2020

@author: 0116092S
"""
import os
import pathlib
from numpy import sqrt, floor, zeros, array, average, amax, amin, mean, poly1d, linspace, loadtxt, transpose, ceil
import copy
import pandas as pd
from matplotlib.pyplot import plot, figure, quiver, gca, boxplot, subplots

import ManuCostModel as man
from ManuCostModel.MapParametersIn import readInputs
from ManuCostModel.MapParametersOut import writeOutputs, sumMats, sumTotals, costResultxml

if __name__ == '__main__':
    
    """
    Read in variables and initialise the manufacturing class object
    """
    
    directory = os.path.dirname(os.path.realpath(__file__))
    
    dirOutputDatabases = "\Output Databases"
    outFileName = '\costOutput.xml'
    outFileName = dirOutputDatabases + outFileName
    
    inputFileName = "manufacturingDatabase"
    
    # Initialise the class
    wingProduction = CostModel.Manufacture(directory, inputFile=inputFileName)
    
    # Analyse the wing manufacturing process
    wingProduction.productionRun(scaling=True)
    
    # Perform production capacity sensitivity analysis
    varStart = 10
    varEnd = 510
    varDelta = 10
    outputLen = int(ceil((varEnd-varStart)/varDelta))
    
    productionCapacity = zeros([outputLen,3])
    count = 0
    
    for var in range(varStart,varEnd,varDelta):
        
        wingProduction.productionVars['General']['ppa'][0] = float(var)
#        ap4.productionVars['General']['salary'][0] = float(var)
        
        wingProduction.productionRun(scaling=False, reSet=True)
       
        productionCapacity[count][0] = var
        productionCapacity[count][1] = wingProduction.manufacturingCosts
        productionCapacity[count][2] = wingProduction.equipmentCosts
        
        count += 1
        
    plot(productionCapacity[:,0], productionCapacity[:,1])
    
    writer = pd.ExcelWriter(directory+'results'+".xlsx", engine='xlsxwriter')
    productionCapacity.to_excel(writer, sheet_name='sheet 1', startrow=0, startcol=0, header=True, index=True)
    writer.save()
    writer.close()
    
    spar1, spar2 = wingProduction.spars
    web1 = wingProduction.webs[0]
    skin1, skin2 = wingProduction.skins
    wing1 = wingProduction.wing[0]
    
    writeOutputs(directory+outFileName, wingProduction)
