# -*- coding: utf-8 -*-
"""
Example script for analysing the variation in wing cost with production capacity

@author: Edward Fagan
"""

import os
from numpy import zeros, ceil
import pandas as pd
import matplotlib.pyplot as plt

import ManuCostModel as mcm
from ManuCostModel.MapParametersOut import writeOutputs

if __name__ == '__main__':
    
    """ Manufacturing analysis """
    
    # Read in variables and initialise the manufacturing class object
    directory = os.path.dirname(os.path.realpath(__file__))
    
    dirOutputDatabases = "\Output Databases"
    outFileName = '\costOutput.xml'
    outFileName = dirOutputDatabases + outFileName
    
    inputFileName = "manufacturingDatabase"
    
    # Initialise the class
    wingProduction = mcm.CostModel.Manufacture(directory, inputFile=inputFileName)
    
    # Analyse the wing manufacturing process
    wingProduction.productionRun(scaling=True)
    
    # Write results to an output database
    writeOutputs(directory+outFileName, wingProduction)
    
    
    """ Sensitivity analysis """
    
    # Perform sensitivity analysis for the production capacity
    varStart = 10
    varEnd = 510
    varDelta = 10
    
    outputLen = int(ceil((varEnd-varStart)/varDelta))
    
    productionCapacity = zeros([outputLen,3])
    
    count = 0
    
    for var in range(varStart,varEnd,varDelta):
        
        wingProduction.productionVars['General']['ppa'][0] = float(var)
        
        wingProduction.productionRun(scaling=False, reSet=True)
       
        productionCapacity[count][0] = var
        productionCapacity[count][1] = wingProduction.manufacturingCosts
        productionCapacity[count][2] = wingProduction.equipmentCosts
        
        count += 1
    
    # Plot results of sensitivity analysis
    plt.plot(productionCapacity[:,0], productionCapacity[:,1])
    plt.xlabel('Production Capacity (ppa)')
    plt.ylabel('Total Wing Cost (€)')
    plt.title('Production Capacity Sensitivity Analysis')
    
    # Export results of sensitivity analysis to excel file
    productionCapacity = pd.DataFrame(productionCapacity)
    
    writer = pd.ExcelWriter(directory+dirOutputDatabases+"\\results.xlsx", engine='xlsxwriter')
    productionCapacity.to_excel(writer, sheet_name='sheet 1', startrow=0, startcol=0, header=True, index=False)
    writer.save()
    
    
    """ General data processing and visualisation """
    
    wingProduction.prodName = 'VI'
    
    plotData1 = mcm.Tools.costCentres(wingProduction, totals=True, stacked=False)
    
    mcm.DataVis.barPlot(plotData1, percentDisplay=False, barLabelDisplay=True)
    
    plotData2 = mcm.Tools.costCentres(wingProduction, totals=True, stacked=True)
    
    mcm.DataVis.pieChart(plotData2)
    