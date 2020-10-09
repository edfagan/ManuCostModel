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
def writeOutputs(outFileName, model):
 
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
    for partKey in model.manufParams.keys():
        for matKey in model.manufParams[partKey]:
            if(matKey in checkSet):
                materialsSet.append(model.manufParams[partKey][matKey])
    
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
    
    # Output the labour results of the cost model
    labOut = ET.SubElement(outFile, 'Labour')
    
    # Include a summary of labour hours and costs
    labSummary = ET.SubElement(labOut, 'summary')
    labCostSummary = ET.SubElement(labSummary, 'costs')
    labCostSummary.set('units', 'euro')
    labHoursSummary = ET.SubElement(labSummary, 'hours')
    labHoursSummary.set('units', 'hours')
    
    for labourVal in model.labourHoursBreakdown.keys():
    
        lab1 = ET.SubElement(labHoursSummary, "parameter")
        lab1.set('name', labourVal)
        lab1.text = form(model.labourHoursBreakdown[labourVal])
        
        lab2 = ET.SubElement(labCostSummary, "parameter")
        lab2.set('name', labourVal)
        lab2.text = form(model.labourCostBreakdown[labourVal])
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
    
    # Output the equipment results of the cost model
    equipOut = ET.SubElement(outFile, 'Equipment')
    
    # Include a summary of equipment costs
    equipSummary = ET.SubElement(equipOut, 'summary')
    equipCostSummary = ET.SubElement(equipSummary, 'costs')
    equipCostSummary.set('units', 'euro')
    
    for equipVal in model.equipmentCostBreakdown.keys():
        
        equip1 = ET.SubElement(equipCostSummary, "parameter")
        equip1.set('name', equipVal)
        equip1.text = form( model.equipmentCostBreakdown[equipVal])
    
    # Build the element tree
    tree = ET.ElementTree(outFile)
    root = tree.getroot()
    
    # Convert to a formatted string
    xmlstr = md.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    
    # Write to the output file
    with open(outFileName,'w') as outf:
        outf.write(xmlstr)


if(__name__ == "__main__"):
    
    source = 'costOutput.xml'
#    
#    totalCost = costResultxml(source)
#    
#    mapMCMoutputs(totalCost)

