#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 22:29:58 2021

@author: edward
"""

import os
import ManuCostModel as man
from ManuCostModel.MapParameters import WriteOutputs
# from ManuCostModel.Tools import BOM
import matplotlib.pyplot as plt
import numpy as np
from numpy import zeros, ceil
import pandas as pd
import sys

directory = os.path.dirname(os.path.realpath(__file__))

dirOutputDatabases = "\Output Databases"
outFileName = '\WingsCosts.xml'

structural_inputs = 'ScalingVariables.xml'

print("\n*********")

print("\t > Structural input data loaded from:", structural_inputs)

inputFileName = "manufacturingDatabase"

VI = man.CostModel.Manufacture(directory, inputFile=inputFileName,
                                processName="VI", productName="wing",
                                scaleFile=structural_inputs)

print("\t > Manufacturing input data loaded from directory:", VI.directory + VI.dirInputDatabases)

VI.ProductionAnalysis(scaling=True, readScaling=True)

optionsList = [VI]

# Determine total costs of manufacturing the RPA
totalCosts = [val.costs_manufacturing for val in optionsList]

print("\t > Analysis completed")

# Write the results to an output file for each production method
for val in optionsList:
    # An inner loop for each of the parts can be inserted here
    outputName = directory+ dirOutputDatabases + "\\" + val.inputFile + "_2024-21-06.xml"
    WriteOutputs(outputName, val)

    print("\t > Results written to:", outputName)
    
print("\t > Manufacturing analysis complete")
print("*********\n")



""" Manufacturing analysis """

# Read in variables and initialise the manufacturing class object
directory = os.path.dirname(os.path.realpath(__file__))

inputFileName = "manufacturingDatabase"

# Initialise the class
wingProduction = man.CostModel.Manufacture(directory, inputFile=inputFileName,
                                processName="VI", productName="wing",
                                scaleFile=structural_inputs)

# Analyse the wing manufacturing process
wingProduction.ProductionAnalysis(scaling=True, readScaling=True)

# Write results to an output database
dirOutputDatabases = "\Output Databases"
outFileName = '\costOutput.xml'
outFileName = dirOutputDatabases + outFileName

WriteOutputs(directory+outFileName, wingProduction)


""" Sensitivity analysis """

# Perform sensitivity analysis for the production capacity
varStart = 10
varEnd = 510
varDelta = 10

outputLen = int(ceil((varEnd-varStart)/varDelta))

productionCapacity = zeros([outputLen,3])

count = 0

for var in range(varStart,varEnd,varDelta):
    
    wingProduction = man.CostModel.Manufacture(directory, inputFile=inputFileName,
                                    processName="VI", productName="wing",
                                    scaleFile=structural_inputs)
    
    wingProduction.productionVars['General']['ppa']['value'] = float(var)
    
    # Reanalyse the production costs, resetting the cost variables each time
    wingProduction.ProductionAnalysis(scaling=True, readScaling=True)
    
    productionCapacity[count][0] = var
    productionCapacity[count][1] = wingProduction.costs_manufacturing
    productionCapacity[count][2] = wingProduction.costs_equipment
    
    count += 1

# Plot results of sensitivity analysis
plt.plot(productionCapacity[0], productionCapacity[1])

plt.xlabel('Production Capacity (ppa)')
plt.ylabel('Total Wing Cost (€)')
plt.title('Production Capacity Sensitivity Analysis')

# Export results of sensitivity analysis to excel file
productionCapacity = pd.DataFrame(productionCapacity)

# writer = pd.ExcelWriter(directory+dirOutputDatabases+"\\results.xlsx", 
#                         engine='xlsxwriter')
# productionCapacity.to_excel(writer, sheet_name='sheet 1', startrow=0, 
#                             startcol=0, header=True, index=False)
# writer.save()
plt.show()

""" General data processing and visualisation """
# # Name the manufacturing anlaysis
# wingProduction.prodName = 'VI'

# # Create a data structure for a bar plot
# plotData1 = man.Tools.CostCentres(wingProduction, totals=True, stacked=False)

# man.DataVis.barPlot(plotData1, percentDisplay=False, barLabelDisplay=True)

# # Create a data structure for a pie chart
# plotData2 = man.Tools.CostCentres(wingProduction, totals=True, stacked=True)

# man.DataVis.pieChart(plotData2)
