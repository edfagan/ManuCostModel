import xml.etree.ElementTree as ET
import xml.dom.minidom as md
import string

# Import cost value from the cost model output database
def costResultxml(source):
    parser = ET.XMLParser(encoding="utf-8")
    src_tree = ET.parse(source, parser=parser)
    src_root = src_tree.getroot()

    wingTotalCost = src_tree.find('.//parameter[@name="total wing cost"]')

    totalCost = wingTotalCost.text

    return totalCost

# Output cost value to the parameters list
def mapMCMoutputs(totalCost):
    
    # Update the parameters list with the new wing cost
    source = 'FC1_Parameters.xml'
    
    src_tree = ET.parse(source)
    
    wingCost = src_tree.find('.//parameter[@name="RPA_AF_MWS_Cost"]')
    wingCostVal = wingCost.find('.//property[@name="value"]')
    
    if(type(totalCost) == 'float'):
        wingCostVal.text = str(round(totalCost, 2))
    else:
        wingCostVal.text = totalCost
    
    src_tree.write(source)

# Format values for output to xml file
def form(inputVal):
    return str(round(inputVal, 2))

# Summing values in a dictionary
def sumTotals(dictTotal):
    
    totalVal = 0.0
    for keyVal in dictTotal.keys():
        for keyVal2 in dictTotal[keyVal].keys():
            totalVal += dictTotal[keyVal][keyVal2]
    
    return round(totalVal, 2)

# Summing values in the materials breakdown dictionary
def sumMats(dictTotal):
    
    totalVal = 0.0
    for keyVal in dictTotal.keys():
        for keyVal2 in dictTotal[keyVal].keys():
            totalVal += sum(dictTotal[keyVal][keyVal2].values())
            
    return round(totalVal, 2)

# Write resutls of the analyses to an xml output database
def writeOutputs(outFileName, ap4Params, materialsCostBreakdown, materialsMassBreakdown, labourCostBreakdown, labourHoursBreakdown, equipmentBreakdown, compSet, structureMass=None):
    
    outFile = ET.Element('outputs')
    outFile.set('model', 'wing cost model results')
    
    # Include the high-level summary of the cost model results
    sumOut = ET.SubElement(outFile, 'Summary')
    
    # Total cost of the wing
    totMatCost = sumMats(materialsCostBreakdown)
    totLabCost = sumTotals(labourCostBreakdown)
    totEquipCost = sumTotals(equipmentBreakdown)
    
    totalWingCost = totMatCost + totLabCost + totEquipCost
    
    sumVals = ET.SubElement(sumOut, "parameter")
    sumVals.set('name', 'total wing cost')
    sumVals.set('units', 'euro')
    sumVals.text = form(totalWingCost)
    
    # Total cost of the materials
    sumVals = ET.SubElement(sumOut, "parameter")
    sumVals.set('name', 'total material costs')
    sumVals.set('units', 'euro')
    sumVals.text = form(totMatCost)
    
    # Total cost of the labour
    sumVals = ET.SubElement(sumOut, "parameter")
    sumVals.set('name', 'total labour costs')
    sumVals.set('units', 'euro')
    sumVals.text = form(totLabCost)
    
    # Total cost of the equipment
    sumVals = ET.SubElement(sumOut, "parameter")
    sumVals.set('name', 'total equipment costs')
    sumVals.set('units', 'euro')
    sumVals.text = form(totEquipCost)
    
    if(structureMass is not None):
        # Total structural mass of the wing
        sumVals = ET.SubElement(sumOut, "parameter")
        sumVals.set('name', 'total wing mass')
        sumVals.set('units', 'kg')
        sumVals.text = form(structureMass)
        
        # Unit production cost of the wing
        sumVals = ET.SubElement(sumOut, "parameter")
        sumVals.set('name', 'unit production cost')
        sumVals.set('units', 'euro/kg')
        sumVals.text = form(totalWingCost/structureMass)
    
    # Output the detailed materials results of the cost model
    matOut = ET.SubElement(outFile, 'Materials')
    
    # Include a summary of materials: mass and costs
    """
    Create a list of all materials present in the wing from ap4Params
    """
    # Create material summary elements
    matSummary = ET.SubElement(matOut, 'summary')
    matSummaryMass = ET.SubElement(matSummary, 'mass')
    matSummaryMass.set('units', 'kg')
    matSummaryCost = ET.SubElement(matSummary, 'cost')
    matSummaryCost.set('units', 'euro')
    
    # Create a list of all materials used in the wing
    materialsSet = []
    checkSet = ['fabric', 'resin', 'hardener', 'prepreg', 'core', 'adhesive', 'coating', 'consumables']
    for partKey in ap4Params.keys():
        for matKey in ap4Params[partKey]:
            if(matKey in checkSet):
                materialsSet.append(ap4Params[partKey][matKey])
    
    materialsSet.append('consumables')
    
    materialsSet = set(materialsSet)
    materialsSet.remove('N/A')
    
    # Update summary with totals for each material
    for materialVal in materialsSet:
        for val1 in materialsCostBreakdown.keys():
            try:
                # Check for consumables before totalling the mass and cost values
                if(materialVal != 'consumables'):
                    sumCostValue = sum(materialsCostBreakdown[val1][materialVal].values())
                    sumMassValue = sum(materialsMassBreakdown[val1][materialVal].values())
                    
                    mat1 = ET.SubElement(matSummaryCost, "parameter")
                    mat1.set('name', materialVal)
                    mat1.text = form(sumCostValue)
                    
                    mat2 = ET.SubElement(matSummaryMass, "parameter")
                    mat2.set('name', materialVal)
                    mat2.text = form(sumMassValue)
                    
                elif(materialVal == 'consumables' and val1 == 'consumables'):
                    sumCostValue = sum([sum(materialsCostBreakdown[val1][i].values()) for i in materialsCostBreakdown[val1]])
                    sumMassValue = sum([sum(materialsMassBreakdown[val1][i].values()) for i in materialsMassBreakdown[val1]])
                
                    mat1 = ET.SubElement(matSummaryCost, "parameter")
                    mat1.set('name', materialVal)
                    mat1.text = form(sumCostValue)
                    
                    mat2 = ET.SubElement(matSummaryMass, "parameter")
                    mat2.set('name', materialVal)
                    mat2.text = form(sumMassValue)
                
                del(sumCostValue)
                del(sumMassValue)
            except:
                pass
    
    materialsList = checkSet
    
    
    
    
    # Iterate through the material categories
    for mat in materialsList:
        # Create a sub-element for the general material category
        matSub = ET.SubElement(matOut, mat)
        
        # Loop through all of the parts in the model
        for compList in compSet:
            
            for compDict in compList:
                
                if(compDict['Materials']['Details'][mat] != 'N/A'):
                    # Add the part sub-element to the list
                    # If no sub-elements exist create one
                    try:
                        # Try find existing parameters
                        matSub.find("parameter").get("name")
                        # Find the parameter sub-element
                        # Check if the individual material type already exists
                        paramName = matSub.findall("parameter")
                        paramList = [i.get("name") for i in paramName]
                        # If the material exists in the output database
                        if(compDict['Materials']['Details'][mat] in paramList):
                            # Find the correct material to add an application
                            for matParam in paramName:
                                # Find the application sub-element
                                if(matParam.get("name") in compDict['Materials']['Details'][mat]):
                                    matApp = matParam.find("application")
                                    # Create a sub-element for this specific part
                                    matAppIndiv = ET.SubElement(matApp, compDict['Name'])
                        else:
                            matElems = ET.SubElement(matSub, "parameter")
                            matElems.set('name',compDict['Materials']['Details'][mat])
                            # Create a sub-element for the parts
                            matApp = ET.SubElement(matElems, "application")
                            # Create a sub-element for this specific part
                            matAppIndiv = ET.SubElement(matApp, compDict['Name'])
                            
                    except AttributeError:
                        # If parameters don't exist create a sub-element for the specific material
                        matElems = ET.SubElement(matSub, "parameter")
                        matElems.set('name',compDict['Materials']['Details'][mat])
                        # Create a sub-element for the parts
                        matApp = ET.SubElement(matElems, "application")
                        # Create a sub-element for this specific part
                        matAppIndiv = ET.SubElement(matApp, compDict['Name'])
                    
                    # Add the mass, cost and scrap percentage figures
                    massVal = compDict['Materials']['Mass'][mat]
                    massScrapVal = compDict['Materials']['Mass Scrap'][mat]
                    
                    costVal = compDict['Materials']['Cost'][mat]
                    costScrapVal = compDict['Materials']['Cost Scrap'][mat]
                    
                    # Total mass and cost values
                    try:
                        matMass = massVal + massScrapVal
                        matCost = costVal + costScrapVal
                    except TypeError:
                        massVal = sum(massVal.values())
                        massScrapVal = sum(massScrapVal.values())
                        costVal = sum(costVal.values())
                        costScrapVal = sum(costScrapVal.values())
                        
                        matMass = massVal + massScrapVal
                        matCost = costVal + costScrapVal
                    
                    # Add values as sub-elements and include units
                    matMassElem = ET.SubElement(matAppIndiv, "property")
                    matMassElem.set('name', 'mass')
                    matMassElem.set('units', 'kg')
                    matMassElem.text = form(matMass)
                    
                    matCostElem = ET.SubElement(matAppIndiv, "property")
                    matCostElem.set('name', 'cost')
                    matCostElem.set('units', 'euro')
                    matCostElem.text = form(matCost)
                        
                    # Check in case total cost value is zero
                    if(matCost > 0.0):
                        # Include the percentage of scrap materials cost
                        scrapCostPerc = costScrapVal/matCost*100.0
                        
                        matCostScrapElem = ET.SubElement(matAppIndiv, "property")
                        matCostScrapElem.set('name', 'cost scrap % (incl.)')
                        matCostScrapElem.set('units', '%')
                        matCostScrapElem.text = form(scrapCostPerc)
                    
                    # Check in case total mass value is zero
                    if(matMass > 0.0):
                        # Include the percentage of scrap materials mass
                        scrapMassPerc = massScrapVal/matMass*100.0
                        
                        matMassScrapElem = ET.SubElement(matAppIndiv, "property")
                        matMassScrapElem.set('name', 'mass scrap % (incl.)')
                        matMassScrapElem.set('units', '%')
                        matMassScrapElem.text = form(scrapMassPerc)
    
    
    
    
    
    # Output the labour results of the cost model
    labOut = ET.SubElement(outFile, 'Labour')
    
    # Include a summary of labour hours and costs
    labSummary = ET.SubElement(labOut, 'summary')
    labCostSummary = ET.SubElement(labSummary, 'costs')
    labCostSummary.set('units', 'euro')
    labHoursSummary = ET.SubElement(labSummary, 'hours')
    labHoursSummary.set('units', 'hours')
    
    for labourVal in labourHoursBreakdown:
        sumHoursValue = sum(labourHoursBreakdown[labourVal].values())
        sumCostValue = sum(labourCostBreakdown[labourVal].values())
    
        lab1 = ET.SubElement(labHoursSummary, "parameter")
        lab1.set('name', labourVal)
        lab1.text = form(sumHoursValue)
        
        lab2 = ET.SubElement(labCostSummary, "parameter")
        lab2.set('name', labourVal)
        lab2.text = form(sumCostValue)
    
    # Breakdown of the individual component labour hours and costs
    for labType in labourHoursBreakdown.keys():
        # Create a sub-element for the labour category
        labElem = ET.SubElement(labOut, "parameter")
        labElem.set("name", labType)
        # Create a sub-element for the applications
        labApp = ET.SubElement(labElem, "application")
        
        for labResult in labourHoursBreakdown[labType].keys():
            
            if(labourHoursBreakdown[labType][labResult] > 0.0):
                # Create a sub-element for each individual part
                labIdvApp = ET.SubElement(labApp, labResult)
                
                # Add the labour hours
                labVal = ET.SubElement(labIdvApp, "property")
                labVal.set('name', 'labour hours')
                labVal.set('units', 'hr')
                labVal.text = form(labourHoursBreakdown[labType][labResult])
                
                # Add the labour costs
                labVal2 = ET.SubElement(labIdvApp, "property")
                labVal2.set('name', 'labour costs')
                labVal2.set('units', 'euro')
                labVal2.text = form(labourCostBreakdown[labType][labResult])
    
    
    # Output the equipment results of the cost model
    equipOut = ET.SubElement(outFile, 'Equipment')
    
    # Include a summary of equipment costs
    equipSummary = ET.SubElement(equipOut, 'summary')
    equipCostSummary = ET.SubElement(equipSummary, 'costs')
    equipCostSummary.set('units', 'euro')
    
    for equipVal in equipmentBreakdown:
        sumValue = sum(equipmentBreakdown[equipVal].values())
        
        equip1 = ET.SubElement(equipCostSummary, "parameter")
        equip1.set('name', equipVal)
        equip1.text = form(sumValue)
    
    # Breakdown of the individual component equipment costs
    for equipType in equipmentBreakdown.keys():
        # Create a sub-element for the equipment category
        equipElem = ET.SubElement(equipOut, "parameter")
        equipElem.set("name", equipType)
        # Create a sub-element for the items
#            equipItem = ET.SubElement(equipElem, "property")
        
        for equipResult in equipmentBreakdown[equipType].keys():
            
            if(equipmentBreakdown[equipType][equipResult] > 0.0):
                # Create a sub-element for each individual part
                equipIdvApp = ET.SubElement(equipElem, 'item')
                
                # Add the labour costs
#                    equipVal1 = ET.SubElement(equipIdvApp, "property")
                equipIdvApp.set('name', equipResult)
                equipIdvApp.set('units', 'euro')
                equipIdvApp.text = form(equipmentBreakdown[equipType][equipResult])
    
    
    # Build the element tree
    tree = ET.ElementTree(outFile)
    root = tree.getroot()
    
    # Convert to a formatted string
    xmlstr = md.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    
    # Write to the output file
    with open(outFileName,'w') as outf:
        outf.write(xmlstr)


# Write resutls of the analyses to an xml output database
def writeOutputs1(outFileName, model):
 
    outFile = ET.Element('outputs')
    outFile.set('model', 'wing cost model results')
    
    # Include the high-level summary of the cost model results
    sumOut = ET.SubElement(outFile, 'Summary')
    
    # Total cost of the wing
    sumVals = ET.SubElement(sumOut, "parameter")
    sumVals.set('name', 'total wing cost')
    sumVals.set('units', 'euro')
    sumVals.text = form(model.manufacturingCosts)
    
    # Total cost of the materials
    sumVals = ET.SubElement(sumOut, "parameter")
    sumVals.set('name', 'total material costs')
    sumVals.set('units', 'euro')
    sumVals.text = form(model.materialCosts)
    
    # Total cost of the labour
    sumVals = ET.SubElement(sumOut, "parameter")
    sumVals.set('name', 'total labour costs')
    sumVals.set('units', 'euro')
    sumVals.text = form(model.labourCosts)
    
    # Total cost of the equipment
    sumVals = ET.SubElement(sumOut, "parameter")
    sumVals.set('name', 'total equipment costs')
    sumVals.set('units', 'euro')
    sumVals.text = form(model.equipmentCosts)
    
    # Total structural mass of the wing
    sumVals = ET.SubElement(sumOut, "parameter")
    sumVals.set('name', 'total wing mass')
    sumVals.set('units', 'kg')
    sumVals.text = form(model.structureMass)
    
    # Unit production cost of the wing
    sumVals = ET.SubElement(sumOut, "parameter")
    sumVals.set('name', 'unit production cost')
    sumVals.set('units', 'euro/kg')
    sumVals.text = form(model.manufacturingCosts/model.structureMass)
    
    # Output the detailed materials results of the cost model
    matOut = ET.SubElement(outFile, 'Materials')
    
    # Create material summary elements
    matSummary = ET.SubElement(matOut, 'summary')
    matSummaryMass = ET.SubElement(matSummary, 'mass')
    matSummaryMass.set('units', 'kg')
    matSummaryCost = ET.SubElement(matSummary, 'cost')
    matSummaryCost.set('units', 'euro')
    
    # Create a list of all materials present in the wing from the input parameters
    materialsSet = []
    checkSet = ['fabric', 'resin', 'hardener', 'prepreg', 'core', 'adhesive', 'coating', 'consumables']
    for partKey in model.ap4Params.keys():
        for matKey in model.ap4Params[partKey]:
            if(matKey in checkSet):
                materialsSet.append(model.ap4Params[partKey][matKey])
    
    materialsSet.append('consumables')
    
    materialsSet = set(materialsSet)
    materialsSet.remove('N/A')
    
    # Update summary with totals for each material
    for materialVal in materialsSet:
        # Check for consumables before totalling the mass and cost values
        if(materialVal != 'consumables'):
            
            mat1 = ET.SubElement(matSummaryCost, "parameter")
            mat1.set('name', materialVal)
            mat1.text = form(model.materialCostBreakdown[materialVal])
            
            mat2 = ET.SubElement(matSummaryMass, "parameter")
            mat2.set('name', materialVal)
            mat2.text = form(model.materialMassBreakdown[materialVal])
            
        elif(materialVal == 'consumables'):
            
            mat1 = ET.SubElement(matSummaryCost, "parameter")
            mat1.set('name', materialVal)
            mat1.text = form(sum(model.consumableCostBreakdown.values()))
            
            mat2 = ET.SubElement(matSummaryMass, "parameter")
            mat2.set('name', materialVal)
            mat2.text = form(sum(model.consumableMassBreakdown.values()))
                

#    
#    materialsList = checkSet
#    
#
#    
#    # Output the labour results of the cost model
#    labOut = ET.SubElement(outFile, 'Labour')
#    
#    # Include a summary of labour hours and costs
#    labSummary = ET.SubElement(labOut, 'summary')
#    labCostSummary = ET.SubElement(labSummary, 'costs')
#    labCostSummary.set('units', 'euro')
#    labHoursSummary = ET.SubElement(labSummary, 'hours')
#    labHoursSummary.set('units', 'hours')
#    
#    for labourVal in labourHoursBreakdown:
#        sumHoursValue = sum(labourHoursBreakdown[labourVal].values())
#        sumCostValue = sum(labourCostBreakdown[labourVal].values())
#    
#        lab1 = ET.SubElement(labHoursSummary, "parameter")
#        lab1.set('name', labourVal)
#        lab1.text = form(sumHoursValue)
#        
#        lab2 = ET.SubElement(labCostSummary, "parameter")
#        lab2.set('name', labourVal)
#        lab2.text = form(sumCostValue)
#    
#    # Breakdown of the individual component labour hours and costs
#    for labType in labourHoursBreakdown.keys():
#        # Create a sub-element for the labour category
#        labElem = ET.SubElement(labOut, "parameter")
#        labElem.set("name", labType)
#        # Create a sub-element for the applications
#        labApp = ET.SubElement(labElem, "application")
#        
#        for labResult in labourHoursBreakdown[labType].keys():
#            
#            if(labourHoursBreakdown[labType][labResult] > 0.0):
#                # Create a sub-element for each individual part
#                labIdvApp = ET.SubElement(labApp, labResult)
#                
#                # Add the labour hours
#                labVal = ET.SubElement(labIdvApp, "property")
#                labVal.set('name', 'labour hours')
#                labVal.set('units', 'hr')
#                labVal.text = form(labourHoursBreakdown[labType][labResult])
#                
#                # Add the labour costs
#                labVal2 = ET.SubElement(labIdvApp, "property")
#                labVal2.set('name', 'labour costs')
#                labVal2.set('units', 'euro')
#                labVal2.text = form(labourCostBreakdown[labType][labResult])
    



if(__name__ == "__main__"):
    
    source = 'costOutput.xml'
#    
#    totalCost = costResultxml(source)
#    
#    mapMCMoutputs(totalCost)

