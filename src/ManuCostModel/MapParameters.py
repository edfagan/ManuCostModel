import xml.etree.ElementTree as ET
import xml.dom.minidom as md
import string

# Import data from parameters list
def apxml(source):
    
    src_tree = ET.parse(source)
    src_root = src_tree.getroot()

    param_name = ''
    
    paramsList = {}
    
    for param in src_root.iter('parameter'):
        param_name = param.attrib['name']
        
        for prop in param.iter('property'):
            if (prop.attrib['name'] == 'value'):
                try:
                    paramsList[param_name] = float(prop.text)
                except:
                    paramsList[param_name] = prop.text

    return paramsList

# Map data from parameters list into the MCM input databases
def mapMCMinputs(paramsList):
    
    # Perform the laminate sizing based on the new system level inputs
    
    # Update the construction input database with the new wing length
    source = 'constructionVariablesDatabase.xml'
    
    src_tree = ET.parse(source)
    
    wingLen = src_tree.find('.//parameter[@name="wing length"]')
    wingVal = wingLen.find('.//property[@name="value"]')
    
    wingVal.text = str(round(paramsList['RPA_AF_MWS_Span'], 2))
    
    src_tree.write(source)


def ReadInputs(manufInputVars, productionVariables, productionMethods, materialVariables, equipmentVariables, consVariables=None):
    """
    Read in the input variables from the xml database files.

    Parameters
    ----------
    manufInputVars : Str
        Manufacturing input database directory and file name.
    productionVariables : Str
        Production variables input database directory and file name.
    productionMethods : Str
        Production methods input database directory and file name.
    materialVariables : Str
        Materials input database directory and file name.
    equipmentVariables : Str
        Equipment input database directory and file name.
    consVariables : Str, optional
        Construction variables input database directory and file name. The default is None.

    Returns
    -------
    params1 : Dict
        Dictionary containing the manufacturing input data.
    params2 : Dict
        Dictionary containing the production variables input data.
    params3 : Dict
        Dictionary containing the production methods input data.
    params4 : Dict
        Dictionary containing the materials input data.
    params5 : Dict
        Dictionary containing the equipment input data.
    params6 : Dict
        Dictionary containing the construction input data.

    """
    
    ## Import the manufacturing input parameters
    params1 = ReadInputsXML(manufInputVars)
    
    # Check database contains input data
    if not params1:
        print('*** Error: Input parameters database file is empty: ', manufInputVars)
    
    ## Import the production variables input parameters
    params2 = ReadInputsXML(productionVariables)
    
    # Check database contains input data
    if not params2:
        print('*** Error: Input parameters database file is empty: ', productionVariables)
    
    ## Import the production methods input parameters
    # Variables that will be saved into the production database
    saveVars1 = ["labourHours", "labourScaling", "staff", "activity", 
                  "capitalEquipment", "materials", "materialScaling", "scrapRate", 
                  "scrapVar", "consumables", "name"]
    
    params3 = ReadInputsXML(productionMethods, saveVars1)
    
    # Check database contains input data
    if not params3:
        print('*** Error: Input parameters database file is empty: ', productionMethods)
    
    ## Import the material input parameters
    # Variables that will be saved into the materials database
    saveVars2 = ["material", "fabric", "resin", "width", "length", "thickness (cured)",
                "areal weight", "cost", "density of fibres", "density of resin",
                "fibre volume fraction", "fibre content", "resin-hardener ratio",
                "thickness", "density", "resin name", "hardener name",
                "fabric name", "cure cycle", "post cure cycle", "resin name", 
                "scaling variable", "scrap_rate", "lineal weight"]
    
    params4 = ReadInputsXML(materialVariables, saveVars2)
    
    # Check database contains input data
    if not params4:
        print('*** Error: Input parameters database file is empty: ', materialVariables)
    
    ## Import the equipment input parameters
    # Variables that will be saved into the equipment database
    saveVars3 = ["purchase cost", "installation cost", "useful life", 
                "salvage value", "floorspace", "machine length", 
                "machine width", "occupancy factor", "scaling variables", 
                "scaling values", "lifetime"]
    
    params5 = ReadInputsXML(equipmentVariables, saveVars3)
    
    # Check database contains input data
    if not params5:
        print('*** Error: Input parameters database file is empty: ', equipmentVariables)
    
    ## Import the construction input parameters
    if consVariables:
        params6 = ReadInputsXML(consVariables)
        
        # Check database contains input data
        if not params6:
            print('*** Error: Input parameters database file is empty: ', consVariables)
    
    else:
        
        params6 = None
    
    return params1, params2, params3, params4, params5, params6


def ReadInputsXML(dataBase, saveList=None):
    """
    Import variables from an xml database.

    Parameters
    ----------
    dataBase : Str
        Database directory and filename.

    Returns
    -------
    params : Dict
        Dictionary of xml data.

    """
    
    # Read values from the input database
    tree = ET.parse(dataBase)
    root = tree.getroot()
    
    # Dictionary to store the variables
    params = {}
    
    if saveList is None:
        saveAll = True
    else:
        saveAll = False
    
    # Iterate thorugh the input parameters and copy values
    for tag in root:
        
        params[tag.attrib['name']] = {}
        
        # Loop through each parameter
        for param in tag.iter('parameter'):
            
            params[tag.attrib['name']][param.attrib['name']] = {}
            
            # If no list of desired properties is defined, save all properties for the parameter
            if saveAll is True:
                saveList = [prop.attrib['name'] for prop in param.iter('property')]
            
            # Loop through each property
            for prop in param.iter('property'):
                
                if (prop.attrib['name'] in saveList):
                    
                    # Check if input value should be converted to float or int (default is string)
                    try:
                        if prop.attrib['type'] == 'double':
                            saveVal = float(prop.text)
                        elif prop.attrib['type'] == 'int':
                            saveVal = int(float(prop.text))
                        elif prop.attrib['type'] == 'vars':
                            saveVal = str.split(prop.text, ', ')
                        elif prop.attrib['type'] == 'list':
                            saveVal = str.split(prop.text, ',')
                            try:
                                saveVal = [float(val) for val in saveVal]
                            except:
                                pass
                        else:
                            saveVal = prop.text
                    except:
                        saveVal = prop.text
                    
                    # Save the value into the input parameters dictionary
                    params[tag.attrib['name']][param.attrib['name']][prop.attrib['name']] = saveVal
                
    return params


def ConsistencyCheck(manufParams, productionVars, productionMethods, materialVars, equipmentVars, consInputVars=None):
    """
    Check the input data is consistent across all input databases.

    Parameters
    ----------
    manufParams : Dict
        Dictionary containing the manufacturing input data.
    productionVars : Dict
        Dictionary containing the production variables input data.
    productionMethods : Dict
        Dictionary containing the production methods input data.
    materialVars : Dict
        Dictionary containing the materials input data.
    equipmentVars : Dict
        Dictionary containing the equipment input data.
    consInputVars : Dict
        Dictionary containing the construction input data. The default is None.

    Returns
    -------
    report : Str
        A report summarising any issues with importing the input databases.

    """
    
    # Create the input data consistency check report
    report = '### Input Data Consistency Check ###\n\n'
    
    # Identify the material categories
    materialCategories = list(materialVars.keys())
    
    # Remove consumables if included in the list
    try:
        materialCategories.remove('consumables')
    except:
        pass
    
    # Create a list of all materials in the materials database
    materialsList = []
    
    for cat in materialCategories:
        
        materialsList = materialsList + list(materialVars[cat].keys())
    
    ## Material variables checks
    report = report + '## Material Data Consistency Check\n'
    
    for component in manufParams.keys():
        
        # List all materials assigned to the component
        mats = [manufParams[component][val] for val in materialCategories if manufParams[component][val] != 'N/A']
        
        for mat in mats:
            if mat not in materialsList:
                report = report + '\t*** Error: material "' + mat + '" for the "' + component + '" component undefined in database\n'
                # pass
            else:
                report = report + '\t"' + mat + '" successfully loaded for the "' + component + '" component\n'
    
    ## Production methods checks
    # Create lists of the production methods and production variables defined in the input databases
    productionMethodsList = list(productionMethods.keys())
    
    productionVariablesList = list(productionVars.keys())
    
    report = report + '\n## Production Method Data Consistency Check\n'
    
    for component in manufParams.keys():
        
        # List all production methods assigned to the component
        product = [manufParams[component][val] for val in ['preforming', 'curing', 'assembly'] if manufParams[component][val] != 'N/A']

        for prod in product:
            if prod not in productionMethodsList or prod not in productionVariablesList:
                report = report + '\t*** Error: production method "' + prod + '" for the "' + component + '" component undefined in database\n'
                # pass
            else:
                report = report + '\t"' + prod + '" successfully loaded for the "' + component + '" component\n'
    
    # Production variables checks
    report = report + '\n## Production Variable Data Consistency Check\n'
    
    for component in manufParams.keys():
        
        # List all production methods assigned to the component
        product = [manufParams[component][val] for val in ['preforming', 'curing', 'assembly'] if manufParams[component][val] != 'N/A']
        
        for prod in product:
            
            # Return all labour scaling values for the component
            labourVars = [productionMethods[prod][step]['labourScaling'][1] for step in productionMethods[prod] if productionMethods[prod][step]['labourScaling'] != 'N/A']
            
            # Check all production variables are present in the database
            failCheck = 0
        
            for var in labourVars:
                
                if var not in productionVars[prod].keys():
                    report = report + '\t*** Error: production variable "' + var + '" for the "' + component + '" component undefined in database\n'
                    failCheck = 1
                    # pass
            
            if failCheck == 0:
                report = report + '\tAll production variables for "' + prod + '" successfully loaded for the "' + component + '" component\n'
            # else:
            #     report = report + '\t*** Error: production variable "' + var + '" for the "' + component + '" component undefined in database\n'
    
    # Equipment variables checks
    report = report + '\n## Equipment Data Consistency Check\n'
    
    # Identify the equipment categories
    equipmentCategories = list(equipmentVars.keys())
    
    # Create a list of all equipment in the database
    dbEquipmentList = [val for eq in equipmentCategories for val in equipmentVars[eq].keys()]
    
    for component in manufParams.keys():
        
        # List all production methods assigned to the component
        product = [manufParams[component][val] for val in ['preforming', 'curing', 'assembly'] if manufParams[component][val] != 'N/A']
        
        for prod in product:
            
            # Return all equipment for the component
            equipList = [productionMethods[prod][step]['capitalEquipment'] for step in productionMethods[prod] if productionMethods[prod][step]['capitalEquipment'] != ['N/A']]
            # Flatten to a single list
            equipList = [val for equip in equipList for val in equip]
            
            # Check all equipment variables are present in the database
            failCheck = 0
            
            for equipItem in equipList:
                
                if equipItem not in dbEquipmentList:
                    report = report + '\t*** Error: equipment variable "' + equipItem + '" for the "' + component + '" component undefined in database\n'
                    failCheck = 1
                    # pass
            
            if failCheck == 0:
                report = report + '\tAll equipment variables for "' + prod + '" successfully loaded for the "' + component + '" component\n'
    
    # Construction variables checks
    
    # Scaling variables checks
    
    return report


def form(inputVal):
    """
    Format values for output to xml file.

    Parameters
    ----------
    inputVal : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return str(round(inputVal, 2))


def SumTotals(dictTotal):
    """
    Summing values in a dictionary.

    Parameters
    ----------
    dictTotal : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    totalVal = 0.0
    for keyVal in dictTotal.keys():
        for keyVal2 in dictTotal[keyVal].keys():
            totalVal += dictTotal[keyVal][keyVal2]
    
    return round(totalVal, 2)


def SumMats(dictTotal):
    """
    Summing values in the materials breakdown dictionary.

    Parameters
    ----------
    dictTotal : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    totalVal = 0.0
    for keyVal in dictTotal.keys():
        for keyVal2 in dictTotal[keyVal].keys():
            totalVal += sum(dictTotal[keyVal][keyVal2].values())
            
    return round(totalVal, 2)


def WriteOutputs(outFileName, model):
    """
    Write results of the analyses to an xml output database.

    Parameters
    ----------
    outFileName : Str
        Path and filename for the output database file.
    model : Obj
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
