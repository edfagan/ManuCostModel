"""

Cost Model Tools

Author: Edward M Fagan

"""

from .DataVis import barPlot

def bom(manuf):
    
    # Determine the bill of materials for manufacturing
    
    pass


def costCentres(manuf, totals=False, stacked=False):
    
    # Example plot for visualising the full breakdown of materials, labour and equipment costs for one production method
    
    
    if totals is False:
        plotInfo = [['Material Cost (€)'],
                    ['Equipment Cost (€)'],
                    ['Labour Cost (€)']]
        
        data = [[[val for val in manuf.materialCategoryCosts.values()]],
                [[val for val in manuf.equipmentItemCosts.values()]],
                [[val for val in manuf.labourCostBreakdown.values()]]]
        
        dataLabels = [[[val for val in manuf.materialCategoryCosts.keys()]],
                      [[val for val in manuf.equipmentItemCosts.keys()]],
                      [[val for val in manuf.labourCostBreakdown.keys()]]]
        
        colourSet = [[['red']],
                     [['green']],
                     [['blue']]]
        
        legendDisplay = [[[1,1,1,1,1]],
                         [[1,1,1,1,1]],
                         [[1,1,1]]]
        
    else:
        if stacked is False:
            plotInfo = [['Material Cost (€)'],
                        ['Equipment Cost (€)'],
                        ['Labour Cost (€)']]
            
            data = [[[sum(manuf.materialCategoryCosts.values())]],
                    [[sum(manuf.equipmentItemCosts.values())]],
                    [[sum(manuf.labourCostBreakdown.values())]]]
            
            dataLabels = [[[manuf.prodName + " Materials"]],
                          [[manuf.prodName + " Equipment"]],
                          [[manuf.prodName + " Labour"]]]
            
            colourSet = [[['red']],
                         [['green']],
                         [['blue']]]
            
            legendDisplay = [[[1]],
                             [[1]],
                             [[1]]]
        else:
            plotInfo = [[manuf.prodName]]
            
            data = [[[sum(manuf.materialCategoryCosts.values()), sum(manuf.equipmentItemCosts.values()), sum(manuf.labourCostBreakdown.values())]]]
            
            dataLabels = [[["Materials", "Equipment", "Labour"]]]
            
            colourSet = [[['red']]]
            
            legendDisplay = [[[1, 1, 1]]]
        
    plotData = plotInfo, data, dataLabels, colourSet, legendDisplay
    
    return plotData
    
if __name__ == '__main__':
    
    manuf.prodName = 'VI'
    
    plotData = costCentres(manuf, totals=True, stacked=False)
    
    barPlot(plotData, percentDisplay=False, barLabelDisplay=True)
