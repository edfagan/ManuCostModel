**********
README.rst
**********

============
Introduction
============

The Manufacturing Cost Model (ManuCostModel) is a python package developed for
technical cost modelling of the manufacturing costs for products made from 
fibre-reinforced composite materials. 

ManuCostModel was developed for a generic aircraft wing design, consisting 
of a structural I-beam spar supporting an aerodynamic skin. The design is also 
applicable to a standard wind turbine blade construction.

.. image:: screengrab.*


============
Installation
============

Installation on Windows: ::

	pip install manucostmodel

=============
Usage Example
=============

The following outlines an example analysis case using ManuCostModel::

	# Import the library
	import ManuCostModel as mcm

	# Provide a path to the directory where the input files can be found
	directory = "...your_path_here"
	
	# Provide a name for the manufacturing database (if different from the default)
	inputFileName = "manufacturingDatabase"

	# Set up the manufacture class object (this can be considered the "factory")
	wingProduction = mcm.CostModel.Manufacture(directory, inputFile=inputFileName)			
	
	# Analyse the production costs
	# scaling is True if the model determines its own geometric scaling variables
	wingProduction.productionRun(scaling=True)
	
	# Use the toolset to create a data object from the analysis results
	plotData = mcm.Tools.costCentres(wingProduction, totals=True, stacked=True)
    
	# Produce a pie chart of the main cost centres for the product
	mcm.DataVis.pieChart(plotData)


=================
Development Setup
=================


===============
Release History
===============

* 0.0.1

	* Work in progress


======================
Contact Info & License
======================

Edward Fagan 

Twitter: @edwardmfagan 

Email: edward_mcm@fastmail.com

This package is distributed under the BSD 3-Clause license. Copyright is held by 
the National University of Ireland Galway 2020. See LICENSE.txt for more information.

============
Contributing
============



