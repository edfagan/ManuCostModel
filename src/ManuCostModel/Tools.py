"""
Cost Model Data Processing Tools

Author: Edward Fagan
"""
import pandas as pd

def BOM(manuf_obj):
    """
    Determine the bill of materials for manufacturing.

    Parameters
    ----------
    manuf_obj : obj
        A manufacturing object.

    Returns
    -------
    bom : DataFrame
        A Pandas dataframe containing the bill of materials.

    """
    
    matCosts = {}
    matName = {}
    
    for val in manuf_obj.breakdown_material_mass_struct.keys():
        
        for matType in manuf_obj.materialVars.keys():
            
            if val in manuf_obj.materialVars[matType].keys():
                
                matCosts[val] = manuf_obj.materialVars[matType][val]['cost']
                matName[val] = manuf_obj.materialVars[matType][val]['material']
                
    bom = pd.DataFrame.from_dict(matName, orient='index', columns=['Material'])
    bom['Unit Cost (€/kg)'] = matCosts.values()
    
    bom['Structural Mass (kg)'] = manuf_obj.breakdown_material_mass_struct.values()
    bom['Structural Cost(€)'] = manuf_obj.breakdown_material_cost_struct.values()
    bom['Scrap Mass (kg)'] = manuf_obj.breakdown_material_mass_scrap.values()
    bom['Scrap Cost(€)'] = manuf_obj.breakdown_material_cost_scrap.values()
    
    bom['Total Mass (kg)'] = bom['Structural Mass (kg)']  + bom['Scrap Mass (kg)']
    bom['Total Cost(€)'] = bom['Structural Cost(€)'] + bom['Scrap Cost(€)']

    return bom

def CostCentres(manuf, totals=False, stacked=False, legendOn=True):
    #
    
    if totals is False:
        plotInfo = [['Material Cost (€)'],
                    ['Equipment Cost (€)'],
                    ['Labour Cost (€)']]
        
        data = [[[val for val in manuf.breakdown_material_categories.values()]],
                [[val for val in manuf.breakdown_equipment_item_cost.values()]],
                [[val for val in manuf.breakdown_labour_cost.values()]]]
        
        dataLabels = [[[val for val in manuf.breakdown_material_categories.keys()]],
                      [[val for val in manuf.breakdown_equipment_item_cost.keys()]],
                      [[val for val in manuf.breakdown_labour_cost.keys()]]]
        
        colourSet = [[['red']],
                     [['green']],
                     [['blue']]]
        
        if legendOn is True:
            legendDisplay = [[[1 for val in range(len(manuf.breakdown_material_categories.keys()))]],
                             [[1 for val in range(len(manuf.breakdown_material_categories.keys()))]],
                             [[1 for val in range(len(manuf.breakdown_material_categories.keys()))]]]
        else:
            legendDisplay = [[[0 for val in range(len(manuf.breakdown_material_categories.keys()))]],
                             [[0 for val in range(len(manuf.breakdown_equipment_item_cost.keys()))]],
                             [[0 for val in range(len(manuf.breakdown_labour_cost.keys()))]]]
        
    else:
        if stacked is False:
            plotInfo = [['Material Cost (€)'],
                        ['Equipment Cost (€)'],
                        ['Labour Cost (€)']]
            
            data = [[[sum(manuf.breakdown_material_categories.values())]],
                    [[sum(manuf.breakdown_equipment_item_cost.values())]],
                    [[sum(manuf.breakdown_labour_cost.values())]]]
            
            dataLabels = [[[manuf.productName + " Materials"]],
                          [[manuf.productName + " Equipment"]],
                          [[manuf.productName + " Labour"]]]
            
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
            plotInfo = [[manuf.productName]]
            
            data = [[[sum(manuf.breakdown_material_categories.values()), sum(manuf.breakdown_equipment_item_cost.values()), sum(manuf.breakdown_labour_cost.values())]]]
            
            dataLabels = [[["Materials", "Equipment", "Labour"]]]
            
            colourSet = [[['red', 'green', 'blue']]]
            
            if legendOn is True:
                legendDisplay = [[[1, 1, 1]]]
            else:
                legendDisplay = [[[0, 0, 0]]]
        
    plotData = plotInfo, data, dataLabels, colourSet, legendDisplay
    
    return plotData

def Compare(productionList, totals=True, stacked=True, oneLegend=True, centreIndex=None):
    """ 
    centreIndex is a integer value referring to a particular Cost Centre 
    Cost Centres are ordered as:
        0 = Materials
        1 = Equipment
        2 = Labour
    """
    plotList = []
    legendOn = True
    
    # Create plot formatted data for each manufacturing analysis
    for prod in productionList:
        
        plotList.append(CostCentres(prod, totals=totals, stacked=stacked, legendOn=legendOn))
        
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
    
# if __name__ == '__main__':
    
    # from DataVis import barPlot
    
    # wingProduction.prodName = 'VI'
    
    # plotData = costCentres(wingProduction, totals=True, stacked=False)
    
    # barPlot(plotData, percentDisplay=False, barLabelDisplay=True)
    
    # plotData = compare([wingProduction, wingProduction, wingProduction], totals=True, stacked=False, centreIndex=2)
    
    # barPlot(plotData, percentDisplay=False, barLabelDisplay=False, secondAxis=True, secondAxisVars=['1','2','3','4','5'])
    
    
    