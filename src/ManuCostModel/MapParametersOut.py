# import xml.etree.ElementTree as ET
from lxml import etree as ET
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

# Write results of the analyses to an xml output database
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


# Write results of the analyses to an xml output database
def manufCostsOut(outFileName, model):
    """
    

    Parameters
    ----------
    outFileName : STR
        Path and filename for the output database file.
    model : OBJECT
        Manufacturing class object.

    Returns
    -------
    None.

    """
    
    productionDetails = model.productName.split("_")
    
    # Set the production method type
    productionType = model.processName
    
    # Set the part name
    partType = model.productName
    try:
        addType = productionDetails[2]
        partType = partType + " " + addType
    except:
        pass
    
    # Check if an output file already exists
    try:
        
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(outFileName, parser)
        
        # tree = ET.parse(outFileName)
        root = tree.getroot()
    except:
        tree = None
        pass
    
    createPart = False
    
    if tree:
        # If the file exsits, check if the value for this part exists in the 
        # file
        for elem in root.find('element'):
            
            if elem.attrib['name'] == partType:
                
                for prop in elem.findall('property'): 
                    
                    if(prop.attrib['name'] ==  'value'):
                        # If the value exists already, update it
                        prop.text = form(model.manufacturingCosts)
                        
         
        partNames = [part.attrib['name'] for part in root.findall('element')]
        
        if partType not in partNames:
            # If the value does not exist, create a new element
            element = ET.SubElement(root, 'element')
            element.set('name', partType)
            
            createPart = True
        
    else:
        # If the file does not exist, create one and create a new element
        outFile = ET.Element('parameters')
        outFile.set('concept', 'AP3_Upscaled')
        
        element = ET.SubElement(outFile, 'element')
        element.set('name', partType)
        
        createPart = True
        
    
    # Populate the rest of the element if needed
    if createPart is True:
        
        parameter = ET.SubElement(element, "parameter")
        parameter.set('name', 'Cost')
        
        property1 = ET.SubElement(parameter, "property")
        property1.set('name', 'description')
        property1.text = partType + " " + productionType + " manufacturing cost"
        
        property2 = ET.SubElement(parameter, "property")
        property2.set('name', 'value')
        property2.text = form(model.manufacturingCosts)
        
        property3 = ET.SubElement(parameter, "property")
        property3.set('name', 'units')
        property3.text = "Euro"
        
        property4 = ET.SubElement(parameter, "property")
        property4.set('name', 'justification')
        property4.text = "Results of manufacturing analysis defined in " + model.inputFile
       
        property5 = ET.SubElement(parameter, "property")
        property5.set('name', 'target')
        property5.text = ""
        
        property6 = ET.SubElement(parameter, "property")
        property6.set('name', 'target_rationale')
        property6.text = ""
        
        property7 = ET.SubElement(parameter, "property")
        property7.set('name', 'min')
        property7.text = ""
        
        property8 = ET.SubElement(parameter, "property")
        property8.set('name', 'probability')
        property8.text = ""
        
        property9 = ET.SubElement(parameter, "property")
        property9.set('name', 'max')
        property9.text = ""
    
    
    if tree:
        
        tree.write(outFileName, encoding='utf-8', pretty_print=True, xml_declaration=True)
        
    else:
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

