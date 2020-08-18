"""

Cost Model Tools

Author: Edward M Fagan

"""

from .DataVis import barPlot

def bom(manuf):
    
    # Determine the bill of materials for manufacturing
    
    pass


def costCentres(manuf):
    
    # Get list of material categories
    materialList = []
    materialCosts = []
    
    for material in manuf.materialVars.items():
        for matKey in material[1]:
            
            if matKey in manuf.materialCostBreakdown.keys():
                
                materialList.append(material[0])
                
    materialList = list(set(materialList))
    
    if sum(manuf.consumableCostBreakdown.values()) > 0.0:
        materiallist.append('consumables')
        
    
    # Example plot for visualising the full breakdown of materials, labour and equipment costs for one production method
    plotInfo = [['Material Cost (€)'],
                ['Equipment Cost (€)'],
                ['Labour Cost (€)']]
    
    data = [[[5000.0, 3155.0, 29.0, 5481.0, 3085.0]],
            [[2500.0, 315.0, 290.0, 548.0, 300.0]],
            [[2500.0, 315.0, 290.0]]]
    
    dataLabels = [[materialList],
                  [["Lifting", "Vacuum", "Mould", "Frame", "Plumbing"]],
                  [["Fabrication", "Finishing", "In-mould"]]]
    
    colourSet = [[['red']],
                 [['green']],
                 [['blue']]]
    
    legendDisplay = [[[1,1,1,1,1]],
                     [[1,1,1,1,1]],
                     [[1,1,1]]]
    
    barPlot(plotInfo, data, dataLabels, colourSet, legendDisplay, percentDisplay=True, barLabelDisplay=True)