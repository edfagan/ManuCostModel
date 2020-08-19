"""

Cost Model Tools

Author: Edward M Fagan

"""

from DataVis import barPlot

def bom(manuf):
    
    # Determine the bill of materials for manufacturing
    
    pass


def costCentres(manuf, totals=False, stacked=False, legendOn=True):
    
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
        
        if legendOn is True:
            legendDisplay = [[[1 for val in range(len(manuf.materialCategoryCosts.keys()))]],
                             [[1 for val in range(len(manuf.materialCategoryCosts.keys()))]],
                             [[1 for val in range(len(manuf.materialCategoryCosts.keys()))]]]
        else:
            legendDisplay = [[[0 for val in range(len(manuf.materialCategoryCosts.keys()))]],
                             [[0 for val in range(len(manuf.equipmentItemCosts.keys()))]],
                             [[0 for val in range(len(manuf.labourCostBreakdown.keys()))]]]
        
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
            
            if legendOn is True:
                legendDisplay = [[[1]],
                                 [[1]],
                                 [[1]]]
            else:
                legendDisplay = [[[0]],
                                 [[0]],
                                 [[0]]]
        else:
            plotInfo = [[manuf.prodName]]
            
            data = [[[sum(manuf.materialCategoryCosts.values()), sum(manuf.equipmentItemCosts.values()), sum(manuf.labourCostBreakdown.values())]]]
            
            dataLabels = [[["Materials", "Equipment", "Labour"]]]
            
            colourSet = [[['red', 'green', 'blue']]]
            
            if legendOn is True:
                legendDisplay = [[[1, 1, 1]]]
            else:
                legendDisplay = [[[0, 0, 0]]]
        
    plotData = plotInfo, data, dataLabels, colourSet, legendDisplay
    
    return plotData

def compare(productionList, totals=True, stacked=True, oneLegend=True, centreIndex=None):
    
    plotList = []
    legendOn = True
    
    # Create plot formatted data for each manufacturing analysis
    for prod in productionList:
        
        plotList.append(costCentres(prod, totals=totals, stacked=stacked, legendOn=legendOn))
        
        if oneLegend is True:
            legendOn = False
    
    # Combine data from each plot
    if stacked is True:
        plotInfo = [entry[0][0] for entry in plotList]
        
        data = [entry[1][0] for entry in plotList]
        
        dataLabels = [entry[2][0] for entry in plotList]
        
        colourSet = [entry[3][0] for entry in plotList]
        
        legendDisplay = [entry[4][0] for entry in plotList]
    
    else:
        plotInfo = plotList[0][0]
        
        data = [i for entry in plotList for val in entry[1] for i in val]
        
        data = [[data[j*3+i] for j in range(int(len(data)/3))] for i in range(3)]
        
        dataLabels = [i for entry in plotList for val in entry[2] for i in val]
        
        dataLabels = [[dataLabels[j*3+i] for j in range(int(len(dataLabels)/3))] for i in range(3)]
        
        colourSet = [i for entry in plotList for val in entry[3] for i in val]
        
        colourSet = [[colourSet[j*3+i] for j in range(int(len(colourSet)/3))] for i in range(3)]
        
        legendDisplay = [i for entry in plotList for val in entry[4] for i in val]
        
        legendDisplay = [[legendDisplay[j*3+i] for j in range(int(len(legendDisplay)/3))] for i in range(3)]
        
        if centreIndex is not None:
            plotInfo = [plotInfo[centreIndex]]
            data = [data[centreIndex]]
            dataLabels = [dataLabels[centreIndex]]
            colourSet = [colourSet[centreIndex]]
            legendDisplay = [legendDisplay[centreIndex]]
            
    plotData = plotInfo, data, dataLabels, colourSet, legendDisplay
    
    return plotData
    
if __name__ == '__main__':
    
    manuf.prodName = 'VI'
    
    plotData = costCentres(manuf, totals=True, stacked=False)
    
    barPlot(plotData, percentDisplay=False, barLabelDisplay=True)
    
    plotData = compare([manuf, manuf, manuf, manuf, manuf], totals=True, stacked=False, centreIndex=2)
    
    barPlot(plotData, percentDisplay=False, barLabelDisplay=False, secondAxis=True, secondAxisVars=['1','2','3','4','5'])
    
    
    