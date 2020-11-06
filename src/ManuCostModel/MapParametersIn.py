import xml.etree.ElementTree as ET
import xml.dom.minidom as md

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

# Read in the primary input variables for construction, production and materials from xml files
def readInputs(manufInputVars, consVariables, productionVariables, productionMethods, materialVariables, equipmentVariables):
    
    # Read values from manufacturing input database
    tree1 = ET.parse(manufInputVars)
    root1 = tree1.getroot()
    
    # Read values from construction input database
    tree2 = ET.parse(consVariables)
    root2 = tree2.getroot()
    
    # Read values from production variables input database
    tree3 = ET.parse(productionVariables)
    root3 = tree3.getroot()
    
    # Read values from production methods input database
    tree4 = ET.parse(productionMethods)
    root4 = tree4.getroot()
    
    # Read values from material input database
    tree5 = ET.parse(materialVariables)
    root5 = tree5.getroot()
    
    # Read values from equipment variables input database
    tree6 = ET.parse(equipmentVariables)
    root6 = tree6.getroot()
    
    # Iterate thorugh the input parameters and copy values
    params1 = {}
    
    # Loop through each component
    for tag in root1:
        # Dictionary to store the variables defining each component and the wing
        params1[tag.attrib['name']] = {}
        # Loop through each parameter
        for param1 in tag.iter('parameter'):
            # Loop through each property
            for prop in param1.iter('property'):
                if (prop.attrib['name'] == 'name'):
                    try:
                        if prop.attrib['type'] == 'double':
                            saveVal = int(float(prop.text))
                        else:
                            saveVal = prop.text
                    except:
                        saveVal = prop.text
                    params1[tag.attrib['name']][param1.attrib['name']] = saveVal
                if (prop.attrib['name'] == 'steps_ignore'):
                    params1[tag.attrib['name']][param1.attrib['name'] +"_"+ prop.attrib['name']] = prop.text.split(", ")
    
    # Iterate thorugh the construction input parameters and copy values
    params2 = {}
    
    # Loop through each component
    for tag in root2:
        # Dictionary to store the variables for (i) the external geometry, 
        # (ii) the internal structure and (iii) other general variables
        params2[tag.attrib['name']] = {}
        # Loop through each parameter
        for param2 in tag.iter('parameter'):
            # Loop through each property
            for prop in param2.iter('property'):
                if (prop.attrib['name'] == 'name'):
                    varName = prop.text
                if (prop.attrib['name'] == 'value'):
                    try:
                        params2[tag.attrib['name']][varName] = float(prop.text)
                    except ValueError:
                        params2[tag.attrib['name']][varName] = prop.text
    
    # Iterate thorugh the production variables input parameters and copy values
    params3 = {}
    
    # Loop through each component
    for tag in root3:
        # Dictionary to store the variables for each production method
        params3[tag.attrib['name']] = {}
        # Loop through each parameter
        for param3 in tag.iter('parameter'):
            varName = param3.attrib['name']
            # Loop through each property
            for prop in param3.iter('property'):
                if (prop.attrib['name'] == 'value'):
                    try:
                        coef, exponent = str.split(prop.text, ',')
                        params3[tag.attrib['name']][varName] = [float(coef), float(exponent)]
                    except ValueError:
                        params3[tag.attrib['name']][varName] = [float(prop.text), 0.0]
    
    # Iterate thorugh the production methods input parameters and copy values
    params4 = {}
    
    # Variables that will be saved into the production database
    saveVars1 = ["labourHours", "labourScaling", "staff", "activity", 
                 "capitalEquipment", "materials", "materialScaling", "scrapRate", 
                 "scrapVar", "consumables", "name"]
    
    # Loop through each component
    for tag in root4:
        # Dictionary to store the production methods
        params4[tag.attrib['name']] = {}
        # Loop through each parameter
        for param4 in tag.iter('parameter'):
            varName = param4.attrib['name']
            # Dictionary to store the steps in each production method
            params4[tag.attrib['name']][varName] = {}
            # Loop through each property
            for prop in param4.iter('property'):
                if (prop.attrib['name'] in saveVars1):
                    
                    if prop.attrib['type'] == 'double':
                        saveVal = float(prop.text)
                    elif prop.attrib['type'] == 'vars':
                        saveVal = str.split(prop.text, ', ')
                    elif prop.attrib['type'] == 'list':
                        saveVal = str.split(prop.text, ',')
                    else:
                        saveVal = prop.text
                        
                        # Remove hack after new model in place
                        if prop.attrib['name'] == 'labourScaling':
                            saveVal = [saveVal]
                        
                    params4[tag.attrib['name']][varName][prop.attrib['name']] = saveVal
    
    # Iterate thorugh the material input parameters and copy values
    params5 = {}
    
    # Variables that will be saved into the materials database
    saveVars2 = ["material", "fabric", "resin", "width", "length", "thickness (cured)",
                "areal weight", "cost", "density of fibres", "density of resin",
                "fibre volume fraction", "fibre content", "resin-hardener ratio",
                "thickness", "density", "resin name", "hardener name",
                "fabric name", "cure cycle", "post cure cycle", "resin name", 
                "scaling variable", "scrap_rate", "lineal weight"]
    
    # Loop through each component
    for tag in root5:
        # Dictionary to store the materials
        params5[tag.attrib['name']] = {}
        # Loop through each parameter
        for param5 in tag.iter('parameter'):
            varName = param5.attrib['name']
            # Dictionary to store the material properties
            params5[tag.attrib['name']][varName] = {}
            # Loop through each property
            for prop in param5.iter('property'):
                if (prop.attrib['name'] in saveVars2):
                    try:
                        params5[tag.attrib['name']][varName][prop.attrib['name']] = float(prop.text)
                    except ValueError:
                        params5[tag.attrib['name']][varName][prop.attrib['name']] = prop.text
                    
    # Iterate thorugh the equipment variables input parameters and copy values
    params6 = {}
    
    # Variables that will be saved into the production database
    saveVars1 = ["purchase cost", "installation cost", "useful life", "salvage value", "floorspace", "machine length", "machine width", "occupancy factor"]
    saveVars2 = ["scaling variables", "scaling values", "lifetime", "floorspace", "machine length", "machine width", "occupancy factor"]
#        saveVars3 = ["machine length", "machine width", "occupancy factor"]
    
    # Loop through each component
    for tag in root6:
        # Dictionary to store the production methods
        params6[tag.attrib['name']] = {}
        # Loop through each parameter
        for param6 in tag.iter('parameter'):
            varName = param6.attrib['name']
            # Dictionary to store the steps in each production method
            params6[tag.attrib['name']][varName] = {}
            # Loop through each property
            for prop in param6.iter('property'):
                # Save different variables for moulds and for regular equipment
                if('tooling_and_moulds' == tag.attrib['name']):
                    if (prop.attrib['name'] in saveVars2):
                        try:
                            if(prop.attrib['name'] in ["machine length", "machine width", "occupancy factor"]):
                                params6[tag.attrib['name']][varName][prop.attrib['name']] = float(prop.text)
                            else:
                                params6[tag.attrib['name']][varName][prop.attrib['name']] = prop.text
                        except:
                            pass
                elif (prop.attrib['name'] in saveVars1):
                    try:
                        params6[tag.attrib['name']][varName][prop.attrib['name']] = float(prop.text)
                    except:
                        
                        params6[tag.attrib['name']][varName][prop.attrib['name']] = prop.text
                        pass
                    
    return params1, params2, params3, params4, params5, params6


def xmlInputs(dataBase):
    
    # Read values from the input database
    tree = ET.parse(dataBase)
    root = tree.getroot()
    params = {}
    
    # Iterate thorugh the input parameters and copy values
    for tag in root:
        # Dictionary to store the variables defining each component and the wing
        params[tag.attrib['name']] = {}
        # Loop through each parameter
        for param in tag.iter('parameter'):
            params[tag.attrib['name']][param.attrib['name']] = {}
            # Loop through each property
            for prop in param.iter('property'):
                # if (prop.attrib['name'] == 'name'):
                    # Check if input value should be converted to a float
                    try:
                        if prop.attrib['type'] == 'double':
                            saveVal = float(prop.text)
                        elif prop.attrib['type'] == 'int':
                            saveVal = int(float(prop.text))
                        else:
                            saveVal = prop.text
                    except:
                        saveVal = prop.text
                    
                    # Save the value into the input parameters dictionary
                    params[tag.attrib['name']][param.attrib['name']][prop.attrib['name']] = saveVal
                
    return params

# def ReadScaling():
    
    