**********
README.rst
**********

============
Introduction
============

The Manufacturing Cost Model (ManuCostModel) is a python package developed for
technical cost modelling of the costs of manufacturing products made primarily from 
fibre-reinforced composite materials. 

ManuCostModel was developed for a generic aircraft wing design, consisting 
of a structural I-beam spar supporting an aerodynamic skin. The design is also 
applicable to standard wind turbine blade construction.

|screengrab|

============
Installation
============

Installation on Windows by cloning the repository::

	# Install the package
	pip install ManuCostModel


==================
Required Libraries
==================

* `numpy <https://numpy.org/>`_
* `scipy <https://www.scipy.org/>`_
* `matplotlib <https://matplotlib.org/>`_
* `pandas <https://pandas.pydata.org/>`_
* `webcolors <https://pypi.org/project/webcolors/>`_
   
=============
Example Usage
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




.. |screengrab| image:: docs/screengrab.png
    :alt: cost breakdown for an aircraft wing
    :scale: 100%


