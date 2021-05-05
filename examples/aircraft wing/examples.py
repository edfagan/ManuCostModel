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
    outputName = directory+ dirOutputDatabases + "\\" + val.inputFile + ".xml"
    WriteOutputs(outputName, val)

    print("\t > Results written to:", outputName)
    
print("\t > Manufacturing analysis complete")
print("*********\n")
