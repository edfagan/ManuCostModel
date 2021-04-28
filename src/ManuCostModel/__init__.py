"""
ManuCostModel
----------

A Python library for performing technical cost modelling of manufacturing
methods for structures made from fibre reinforced composite materials. 

Modules include:
    
    :mod:`ManuCostModel.CostModel`
        The `.CostModel` class for all cost calculations.
        
    :mod:`ManuCostModel.PartDecomposition`
        The `.PartDecomposition` class for calculating geometric scaling 
        variables from standard part definitions (spars, webs, skins, etc.)
        
    :mod:`ManuCostModel.MapParametersIn`
        The `.MapParametersIn` class for importing xml databases.
        
    :mod:`ManuCostModel.MapParametersOut`
        The `.MapParametersOut` class for exporting xml databases.
        
    :mod:`ManuCostModel.Tools`
        The `.Tools` class for additional data processing tools.
        
    :mod:`ManuCostModel.DataVis`
        The `.DataVis` class for data useful visualisation options.
        
    :mod:`ManuCostModel.LaminateSizing`
        The `.LaminateSizing` class for determining laminate thicknesses.
        
ManuCostModel is written and maintained by Edward Fagan.
        
"""
from . import DataVis, LaminateSizing, CostModel, MapParameters, PartDecomposition, Tools