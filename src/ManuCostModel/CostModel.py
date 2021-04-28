"""
Manufacturing Cost Model
----------

The cost model is structured around three class types:
    
    1. A component class is used to store information and perform calculations 
    on the "part" level. The component class object has its own internal classes 
    for specific cost centres, including materials, labour and equipment.

    2. A production step class is used to store information on a single step in
    the manufacturing approach.

    3. A manufacturing class is used to perform calculations on all of the parts.
    It can be considered as the "factory" level.
    
"""

import os
from numpy import loadtxt, ceil, array
import copy
from .MapParameters import ReadInputs, ReadInputsXML, ConsistencyCheck
from .PartDecomposition import ScalingVariables, AssemblyScaling


class component:
    """
    Class for creating component objects.

    Parameters
    ----------
    partName : str
        Name of the part
        
    partType : str
        Type of part, must match an element from the manufacturing database.
        Current options include: 'spar', 'web', 'skin' and 'wing'
        
    matDetails : dict, default None
        Dictionary identifying the materials present in the part and the names
        of those materials.
        Keys must match elements from the materials database and elements must
        match associated parameter names from the materials database
        
    partBrand : str, default 'preform'
        Identifier of the type of manufacturing operation, current options 
        include 'preform' or 'assembly'
        
    activityLevels : list[str], default ['manufacturing']
        A list of the different activities the cost centres are associated with.
        Options are customisable and can be found in the "activity" property
        of the production methods database. Current options include: 'preform',
        'cure', 'assembly', and 'finishing'

    Notes
    -----
    Comments are under development

    Examples
    --------
    Default usage:

    >>> spar = component('Upper Spar', 
                         'spar', 
                         matDetails={'fabric':'Saertex UD'}, 
                         partBrand='preform', 
                         activityLevels=['preforming', 'curing', 
                                         'assembly'])
    """
    
    def __init__(self, partName, partType, productName, matDetails=None, partBrand='preform', activityLevels=['Manufacturing']):
        """
        

        Parameters
        ----------
        partName : TYPE
            DESCRIPTION.
        partType : TYPE
            DESCRIPTION.
        matDetails : TYPE, optional
            DESCRIPTION. The default is None.
        partBrand : TYPE, optional
            DESCRIPTION. The default is 'preform'.
        activityLevels : TYPE, optional
            DESCRIPTION. The default is ['Manufacturing'].

        Returns
        -------
        None.

        """
        # General object variables
        self.name = partName
        self.type = partType
        self.brand = partBrand
        self.product = productName
        
        self.scaleVars = {}
        self.productionSteps = []
        self.productionNames = []
        
        self.activityLevels = activityLevels
        
        # Material variables
        self.matDetails = matDetails
        self.materials = self.Materials(self.matDetails)
        self.consumables = self.Materials()
        
        # Labour variables
        self.labour = self.Labour()
        
        # Equipment variables
        self.equipment = self.Equipment(self.activityLevels)
        
        # Building variables
        self.spaceReqs = []
        
        
    
    def EmptyDict(self, dictVars, newDict={}):
        """
        Method for resetting dictionaries to zeros or for setting up a new 
        empty dictionary

        Parameters
        ----------
        dictVars : TYPE
            DESCRIPTION.
        newDict : TYPE, optional
            DESCRIPTION. The default is {}.

        Returns
        -------
        newDict : TYPE
            DESCRIPTION.

        """
        
        for val in iter(dictVars):
            newDict[val] = 0.0
            
        return newDict
    
    
    def ProductionStepDefinition(self, productionDict, append=True):
        """
        Method to populate a list of production steps

        Parameters
        ----------
        productionDict : TYPE
            DESCRIPTION.
        append : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        """
        
        if append is False:
            self.productionSteps = []
        
        # Create a list of production steps
        for label in productionDict:
            
            stepInstance = self.ProductionStep()
            stepInstance.stepLabel = label
            
            for stepVar in productionDict[label]:
                
                try:
                    # Check if the member exists
                    getattr(stepInstance, stepVar)
                    
                    # If data exist for the member in the input database add them
                    if productionDict[label][stepVar] != 'N/A':
                        setattr(stepInstance, stepVar, productionDict[label][stepVar])
                        
                except AttributeError:
                    pass
                    
            self.productionSteps.append(stepInstance)
        
        # Populate the list of equipment for the production steps
        self.equipment.LocateEquipment(self.productionSteps)
    
    def ProductionDefinition(self, inputParams, productionMethods):
        """
        

        Parameters
        ----------
        inputParams : TYPE
            DESCRIPTION.
        productionMethods : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        paramData = inputParams[self.type]
        
        productionCategory = ['preforming', 'curing', 'assembly']
        
        for catName in productionCategory:
            try:
                activityName = paramData[catName]
                
                if activityName != 'N/A':
                    activitySteps = copy.deepcopy(productionMethods[activityName])
                    
                    try:
                        stepsIgnore = paramData[catName+'_steps_ignore']
                        for step in stepsIgnore:
                            del(activitySteps[step])
                    except:
                        pass
                    
                    try:
                        self.ProductionStepDefinition(activitySteps, append=True)
                    except:
                        self.ProductionStepDefinition(activitySteps, append=False)
                    
                    self.productionNames = self.productionNames + [activityName for i in range(len(activitySteps))]
                    
            except:
                pass
            
    
    class Materials:
        """
        Internal class for material cost centre related functions and variables.
        
        Parameters
        ----------
        matDetails : dict, default None
            Dictionary identifying the materials present in the part and the names
            of those materials.
            Keys must match elements from the materials database and elements must
            match associated parameter names from the materials database
        """
        
        def __init__(self, matDetails=None):
            # Define material variables
            self.mass = {}
            self.matCost = {}
            self.massScrap = {}
            self.matCostScrap = {}
            
            self.cost = 0.0
            self.materialMass = 0.0
            
            # Populate the Materials object if inputs are available
            if matDetails is not None:
                if type(matDetails) is dict:
                    self.DictionaryUpdate(matDetails)
                
                elif type(matDetails) is str or list:
                    self.MaterialAdd(matDetails)
        
        def MaterialDict(self, matDict, matDetails):
            """
            Method for populating a dictionary with zeros

            Parameters
            ----------
            matDict : TYPE
                DESCRIPTION.
            matDetails : TYPE
                DESCRIPTION.

            Returns
            -------
            None.

            """
            
            for val in iter(matDetails):
                matDict[val] = 0.0
                
        
        def DictionaryUpdate(self, matDetails):
            """
            Method for populating all dictionaries with zeros and adding new 
            elements

            Parameters
            ----------
            matDetails : TYPE
                DESCRIPTION.

            Returns
            -------
            None.

            """
            for obj in [self.mass, self.matCost, self.massScrap, self.matCostScrap]:
                self.MaterialDict(obj, matDetails)
        
        
        def MaterialAdd(self, materials):
            """
            Method for adding a new material or list of materials

            Parameters
            ----------
            materials : TYPE
                DESCRIPTION.

            Returns
            -------
            None.

            """
            tempDict = {}
            
            # Check for single item or list for addition
            if type(materials) is str:
                materials = [materials]
            
            # Create dummy dictionary
            for mats in materials:
                tempDict[mats] = 'N/A'
            
            self.DictionaryUpdate(tempDict)
        
        
        def TotalMass(self, structureMass=False):
            """
            Method for summing up the total mass

            Parameters
            ----------
            structureMass : TYPE, optional
                DESCRIPTION. The default is False.

            Returns
            -------
            TYPE
                DESCRIPTION.

            """
            if structureMass is False:
                self.materialMass = sum(self.mass.values()) + sum(self.massScrap.values())
            elif structureMass is True:
                return sum(self.mass.values())
        
        
        def TotalCost(self):
            """
            Method for summing up the total costs

            Returns
            -------
            None.

            """
            self.cost = sum(self.matCost.values()) + sum(self.matCostScrap.values())
        
    class Labour:
        """
        Internal class for labour cost centre related functions and variables.
        
        Parameters
        ----------
        numSteps : int, default None
            Number of steps in the production method
            
        activities : list[str,str,...], default None
            A list of the different activities the cost centres are associated with.
            Options are customisable and can be found in the "activity" property
            of the production methods database. Current options include: 'preform',
            'cure', 'assembly', and 'finishing'
        """
        
        def __init__(self, numSteps=None, activities=None):
            # Make these into dictionaries to capture the values for each step
            if numSteps is None:
                self.processHours = []
                self.labourHours = []
                self.labourCosts = []
            else:
                self.processHours = [0.0 for i in range(numSteps)]
                self.labourHours = [0.0 for i in range(numSteps)]
                self.labourCosts = [0.0 for i in range(numSteps)]
            
            self.activityCosts = {}
            self.activityHours = {}
            
            if activities is not None:
                self.ActivityDict(activities, self.activityCosts)
                self.ActivityDict(activities, self.activityHours)
        
        
        def ActivityDict(self, activityLevels, labourDict):
            """
            

            Parameters
            ----------
            activityLevels : TYPE
                DESCRIPTION.
            labourDict : TYPE
                DESCRIPTION.

            Returns
            -------
            None.

            """
            for act in activityLevels:
                labourDict[act] = 0.0
            
        
        def TotalCost(self):
            """
            Method for summing up the results

            Returns
            -------
            None.

            """
            self.totalProcessHours = sum(self.processHours)
            self.totalLabourHours = sum(self.labourHours)
            self.totalCost = sum(self.labourCosts)
    
    class Equipment:
        """
        Internal class for equipment cost centre related functions and variables.
        
        Parameters
        ----------
        activityLevels : list[str,str,...], default None
            A list of the different activities the cost centres are associated with.
            Options are customisable and can be found in the "activity" property
            of the production methods database. Current options include: 'preform',
            'cure', 'assembly', and 'finishing'
        """
        
        def __init__(self, activityLevels):
            # Make these into dictionaries to capture the values for each step
            self.equipmentList = {}
            self.equipmentCosts = {}
            self.powerCosts = {}
            self.activityCosts = {}
            
            self.ActivityDict(activityLevels, self.equipmentList)
            self.ActivityDict(activityLevels, self.activityCosts)
            
            self.cost = 0.0
            self.power = 0.0
            
            
        def ActivityDict(self, activityLevels, equipDict):
            """
            

            Parameters
            ----------
            activityLevels : TYPE
                DESCRIPTION.
            equipDict : TYPE
                DESCRIPTION.

            Returns
            -------
            None.

            """
            for act in activityLevels:
                equipDict[act] = []
            
        
        def LocateEquipment(self, productionSteps):
            """
            A method to populate the dictionaries

            Parameters
            ----------
            productionSteps : TYPE
                DESCRIPTION.

            Returns
            -------
            None.

            """
            
            try:
                fullList = [val.capitalEquipment for val in iter(productionSteps)]
                activityList = [val.activity for val in iter(productionSteps)]
                
                for i, activity in enumerate(activityList):
                    if fullList[i][0] != 'N/A':
                        self.equipmentList[activity] += fullList[i]
                        
                        for equip in fullList[i]:
                            if equip != 'N/A':
                                self.equipmentCosts[equip] = 0.0
                                self.powerCosts[equip] = 0.0
            
            except:
                pass
        
        
        def TotalCost(self):
            """
            Method for summing up the total costs

            Returns
            -------
            None.

            """
            self.cost = sum(self.equipmentCosts.values())
            self.power = sum(self.powerCosts.values())


    class ProductionStep:
        """
        """
        def __init__(self):
            
            self.stepLabel = None
            self.name = None
            self.labourScaling = None
            self.labourHours = None
            self.staff = None
            self.activity = None
            self.capitalEquipment = None
            self.materials = None
            self.materialScaling = None
            self.scrapRate = None
            self.scrapVar = None
            self.consumables = None


class Manufacture:
    """ 
    Class for creating Manufacture objects.

    Parameters
    ----------
    directory : str
        Path to the directory where the input databases are located.
        
    inputFile : str
        Name of the name of the manufacturing database file.
        
    productName : str, optional
        Optional name for identifying the product. Used for naming data series 
        and data visualisation.
        
    processName : str, optional
        Optional name for identifying the manufacturing process. Used for 
        naming data series and data visualisation.

    scaleFile : str
        Optional name for identifying the scaling variables.
    """
    
    def __init__(self, directory, inputFile, productName='', processName='', scaleFile=''):
        
        # Store the input variables
        self.directory = directory
        self.inputFile = inputFile
        self.productName = productName
        self.processName = processName
        
        # Directory locations
        self.CSVloc = "CSV Files\\"
        self.dirInputDatabases = "\\Input Databases\\"
        self.dirOutputDatabases = "\\Output Databases\\"
        
        # Create a directory for model results
        try:
            os.mkdir(self.directory+self.dirOutputDatabases)
        except FileExistsError:
            pass
        
        ## Import the input databases
        if len(inputFile) == 0:
            # Default manufacturing inputs database name
            self.inputFile = "manufacturingDatabase"
        
        # Add directory locations to the file names
        manufacturingInputVars = self.directory + self.dirInputDatabases + self.inputFile + ".xml"
        consVariables = self.directory + self.dirInputDatabases + "constructionVariablesDatabase.xml"
        productionVariables = self.directory + self.dirInputDatabases + "productionVariablesDatabase.xml"
        productionMethods = self.directory + self.dirInputDatabases + "productionMethodsDatabase.xml"
        materialVariables = self.directory + self.dirInputDatabases + "materialsDatabase.xml"
        equipmentVariables = self.directory + self.dirInputDatabases + "equipmentVariablesDatabase.xml"
        
        # Check if the filename for the scaling variables has been entered
        if type(scaleFile) is str:
            self.scalingInputVariables = self.dirInputDatabases + scaleFile
            
        # Or a dictionary of the scaling variable data
        elif type(scaleFile) is dict:
            self.scalingInputVariables = scaleFile
        
        # Import the data
        self.manufacturingDB, self.productionVars, self.productionMethods, self.materialVars, self.equipmentVars, self.consInputVars = ReadInputs(manufacturingInputVars, productionVariables, productionMethods, materialVariables, equipmentVariables, consVariables)
        
        # Create component objects for each part defined in the manufacturing input file
        self.activityLevels = ['preform', 'cure', 'assembly', 'finishing']
        self.brandTypes = {'spar': 'preform', 'web': 'preform', 'skin': 'preform', 'wing': 'assembly'}
        
        # Create parts and assembly lists
        self.parts = []
        self.assemblies = []
        
        # Note: Hack so that only the first assembly in the manufacturing input database is assessed
        # self.manufParams = self.manufacturingDB[list(self.manufacturingDB.keys())[0]]
        
        # Create components based on manufacturing input database
        for productKey in self.manufacturingDB.keys():
            
            manufParams = self.manufacturingDB[productKey]
            
            for key in manufParams.keys():
                    
                keyname = str(key)
                
                try:
                    brandName = self.brandTypes[keyname]
                except KeyError:
                    if 'assembly' in keyname:
                        brandName = 'assembly'
                    else:
                        brandName = 'preform'
                
                newPart = self.SetComponents(manufParams, productKey, self.activityLevels, keyname, brandName, manufParams[keyname]['# items'])
                
                # Add the new components to either assembly or part lists
                if manufParams[key]['assembly'] != 'N/A':
                    
                    self.assemblies.append(newPart)
                    
                else:
                    
                    self.parts.append(newPart)
        
        # Create the combined list of all components in the analysis
        self.partsList = self.parts + self.assemblies
        
        # Create manufacturing results variables
        self.equipmentList = {}
        self.productLines = {}
        self.assemblyLines = {}
        self.commonEquipment = {}
        self.costs_manufacturing = 0.0
        self.costs_materials = 0.0
        self.costs_labour = 0.0
        self.costs_equipment = 0.0
        self.costs_overheads = 0.0
        self.cost_building = 0.0
        self.structure_mass = 0.0
        self.unit_cost = 0.0
        
        self.analysis_report = ConsistencyCheck(self.manufacturingDB, self.productionVars, self.productionMethods, self.materialVars, self.equipmentVars, self.consInputVars)
        
        # if self.consInputVars:
        #     self.csvFileName()
    
    
    def csvFileName(self):
        """
        Add the material names to the part thickness csv file names (deprecated)

        Returns
        -------
        None.

        """
        
        try:
            if(self.manufParams['spar']['fabric'] != 'N/A'):
                sparMatName = self.manufParams['spar']['fabric']
            else:
                sparMatName = self.manufParams['spar']['prepreg']
                
            self.consInputVars['internal_structure']['sparThick'] = sparMatName + "_" + self.consInputVars['internal_structure']['sparThick']
        except:
            pass
        
        try:
            if(self.manufParams['web']['fabric'] != 'N/A'):
                webMatName = self.manufParams['web']['fabric']
            else:
                webMatName = self.manufParams['web']['prepreg']
                
            self.consInputVars['internal_structure']['webThick'] = webMatName + "_" + self.consInputVars['internal_structure']['webThick']
        except:
            pass
        
        try: 
            if(self.manufParams['skin']['fabric'] != 'N/A'):
                skinMatName = self.manufParams['skin']['fabric']
            else:
                skinMatName = self.manufParams['skin']['prepreg']
            
            self.consInputVars['internal_structure']['skinThick'] = skinMatName + "_" + self.consInputVars['internal_structure']['skinThick']
        except:
            pass
    
    
    def ResetManufacture(self):
        """
        Method for resetting all objects and results variables to their default state

        Returns
        -------
        None.

        """
        # Reset all components to their default state
        reSetCheck = [self.ResetComponents(part, self.manufacturingDB, self.activityLevels) for part in self.partsList]
        
        # Reset all manufacturing results to zero or empty
        self.productLines = {}
        self.assemblyLines = {}
        self.commonEquipment = {}
        self.costs_manufacturing = 0.0
        self.costs_materials = 0.0
        self.costs_labour = 0.0
        self.costs_equipment = 0.0
        self.structure_mass = 0.0
        self.unit_cost = 0.0
        
    
    def SetComponents(self, manufParams, productKey, activityLevels, partName, brand, numParts):
        """
        Method for creating a list of component objects

        Parameters
        ----------
        manufParams : Dict
            DESCRIPTION.
        activityLevels : List
            DESCRIPTION.
        partName : Str
            DESCRIPTION.
        brand : Str
            DESCRIPTION.
        numParts : Int
            DESCRIPTION.

        Returns
        -------
        list
            DESCRIPTION.

        """
        return [component(partName+str(i+1), partName, productKey, matDetails=self.MaterialDictionary(manufParams, partName), partBrand=brand, activityLevels=activityLevels) for i in range(numParts)]
    
    
    def ResetComponents(self, compList, manufacturingDB, activityLevels):
        """
        

        Parameters
        ----------
        compList : TYPE
            DESCRIPTION.
        manufParams : TYPE
            DESCRIPTION.
        activityLevels : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        for comp in compList:
            scalingVars = copy.deepcopy(comp.scaleVars)
            manufParams = manufacturingDB[comp.product]
            comp.__init__(comp.name, comp.type, self.MaterialDictionary(manufParams, comp.type), partBrand=self.brandTypes[comp.type], activityLevels=activityLevels)
            comp.scaleVars = copy.deepcopy(scalingVars)
        
    
    def MaterialDictionary(self, manufParams, partType):
        """
        Create a dictionary of the materials and material categories for a part

        Parameters
        ----------
        manufParams : TYPE
            DESCRIPTION.
        partType : TYPE
            DESCRIPTION.

        Returns
        -------
        MaterialsDict : TYPE
            DESCRIPTION.

        """
        materialCategories = ['fabric', 'resin', 'hardener', 'prepreg', 'core', 'adhesive', 'coating']
        materialDetails = {}
        
        for val in manufParams[partType]:
            if val in materialCategories:
                if manufParams[partType][val] != 'N/A':
                    materialDetails[val] = manufParams[partType][val]
        
        return materialDetails
    

    def Scale(self, readFile=False):
        """
        

        Parameters
        ----------
        readFile : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        None.

        """
        directory = self.directory + self.dirInputDatabases + self.CSVloc
        
        # Default is to calculate scaling variables from structural and 
        # geometric parameters
        if readFile is False:
            for compList in self.parts:
                for comp in compList:
                    ScalingVariables(comp, directory, self.consInputVars, self.materialVars)
        
            AssemblyScaling(self.skins, self.webs, self.wing[0])
            
        # Otherwise read in predefined values from an input database
        else:
            # Read from an input database unless the data is already entered as a dict
            if type(self.scalingInputVariables) is str:
                scalingInputs = ReadInputsXML(self.directory + self.scalingInputVariables)
                
            elif type(self.scalingInputVariables) is dict:
                scalingInputs = self.scalingInputVariables
            
            # Apply the scaling variables to each part
            for prod in self.manufacturingDB.keys():
                
                for compList in self.partsList:
                    
                    for comp in compList:
                        
                        try:
                            comp.scaleVars = scalingInputs[prod][comp.name]
                        except:
                            pass
    
    
    def DepreciationCost(self, equipName):
        """
        Calculates the annual portion of depreciation for a piece of equipment

        Parameters
        ----------
        equipName : TYPE
            DESCRIPTION.

        Returns
        -------
        annualDepr : TYPE
            DESCRIPTION.

        """
        equipVariables = self.equipmentVars['capital_equipment'][equipName]
        
        purchaseVal = equipVariables['purchase cost']
        installFactor = equipVariables['installation cost']/100.0 + 1.0
        usefulLife = equipVariables['useful life']
        salvageVal = equipVariables['salvage value']
        
        annualDepr = (purchaseVal*installFactor - salvageVal)/usefulLife
        
        return annualDepr
    
    
    def BuildingCost(self, equipName, partName):
        """
        Method for calculating the building costs

        Parameters
        ----------
        equipName : TYPE
            DESCRIPTION.
        partName : TYPE
            DESCRIPTION.

        Returns
        -------
        floorArea : TYPE
            DESCRIPTION.

        """
        equipVariables = self.equipmentVars['capital_equipment'][equipName]
        
        if(equipVariables['floorspace'] == "N/A"):
            floorArea = 0.0
            
        elif(equipVariables['floorspace'] == "calculation"):
            length = equipVariables['machine length']
            width = equipVariables['machine width']
            floorArea = length*width
            
        elif(equipVariables['floorspace'] == "Surface Area"):
            if('wing' in partName):
                floorArea = self.scalingVars[partName][partName]['Surface Area']
            else:
                partType = partName[:-1]
                floorArea = self.scalingVars[partType][partName]['Surface Area']
            
        elif(equipVariables['floorspace'] == "wingLen"):
            length = self.consInputVars['external_geometry']['wingLen']
            width = 2.5
            floorArea = length*width
            
        return floorArea
    
    
    def ProductionAnalysis(self, scaling=True, readScaling=False, reSet=False):
        """
        A method for performing the manufacturing analysis

        Parameters
        ----------
        scaling : BOOLEAN, optional
            scaling determines if the scaling calculation is performed 
            (default option) or not. The default is True.
        readScaling : BOOLEAN, optional
            readScaling determines if the scaling values are calculated within
            the model (default option) or read from a file. The default is False.
        reSet : BOOLEAN, optional
            The default is False.
        
        Returns
        -------
        None.
        """
        # Reset components and results variables 
        if reSet is True:
            self.ResetManufacture()
        
        # Determine the scaling variables
        if scaling is True:
            self.Scale(readScaling)
        
        # Analyse the part material and labour costs
        for compList in self.partsList:
            
            for comp in compList:
                manufParams = self.manufacturingDB[comp.product]
                comp.ProductionDefinition(manufParams, self.productionMethods)
                
                self.PartAnalysis(comp, self.materialVars, self.productionVars, runEquip=False)
        
        # Determine the number of part and assembly production lines
        if len(self.productLines.keys()) == 0:
            self.ProductionLines(self.productLines, self.productionVars, lineType='preform')
        
        if len(self.assemblyLines.keys()) == 0:
            self.ProductionLines(self.assemblyLines, self.productionVars, lineType='assembly')
        
        # Determine the equipment shared across the facility
        self.CommonEquipment(self.partsList)
        
        # Analyse the part equipment costs
        for compList in self.partsList:
            
            for comp in compList:
            
                self.PartAnalysis(comp, self.materialVars, self.productionVars, runMats=False, runLab=False)
        
        # Determine the total costs of manufacturing
        self.TotalCosts()
        
        
    def PartAnalysis(self, comp, materialVars, productionVars, runMats=True, runLab=True, runEquip=True):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.
        materialVars : TYPE
            DESCRIPTION.
        productionVars : TYPE
            DESCRIPTION.
        runMats : TYPE, optional
            DESCRIPTION. The default is True.
        runLab : TYPE, optional
            DESCRIPTION. The default is True.
        runEquip : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        """
        
        if runMats is True:
            self.MaterialsAnalysis(comp, materialVars)
        
        if runLab is True:
            self.LabourAnalysis(comp, materialVars, productionVars)
            self.LabourActivity(comp)
        
        if runEquip is True:
            # Labour calculations must be conducted before the number of manufacturing
            # lines and hence equipment costs can be determined
            try:
                self.EquipmentAnalysis(comp)
            except:
                print('***** Error: No production line data available')
                pass
        
        
    def MaterialsAnalysis(self, comp, materialVars):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.
        materialVars : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        productSteps = comp.productionSteps
        
        # Run through steps in production
        for i, step in enumerate(productSteps):
            
            # Determine material costs
            if step.materials is not None:
                
                self.MaterialsCost(comp, materialVars, i)
            
            # Determine consumables costs
            if step.consumables[0] != 'N/A':
                
                self.ConsumablesCost(comp, materialVars, i)
                
        comp.materials.TotalCost()
        comp.materials.TotalMass()
        comp.consumables.TotalCost()
    
    
    def LabourAnalysis(self, comp, materialVars, productionVars):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.
        materialVars : TYPE
            DESCRIPTION.
        productionVars : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        productSteps = comp.productionSteps
        
        comp.labour = comp.Labour(len(productSteps), activities=self.activityLevels)
        
        # Run through steps in production
        for i, step in enumerate(productSteps):
            
            # Determine labour costs
            self.LabourCost(comp, materialVars, productionVars, i)
            
        comp.labour.TotalCost()
    
    
    def EquipmentAnalysis(self, comp):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        productSteps = comp.productionSteps
        
        # Run through steps in production
        for i, step in enumerate(productSteps):
            
            # Determine the equipment costs
            if step.capitalEquipment[0] != 'N/A':
                
                self.EquipmentCost(comp, i)
                
        comp.equipment.TotalCost()
    

    def MatCheck(self, value, variableName):
        """
        material cost methods

        Parameters
        ----------
        value : TYPE
            DESCRIPTION.
        variableName : TYPE
            DESCRIPTION.

        Returns
        -------
        value : TYPE
            DESCRIPTION.

        """
        
        if variableName == 'density':
            value = value
        else:
            value = value/1000.0
            
        return value
    
    
    def MaterialsCost(self, comp, materialVars, stepNum):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.
        materialVars : TYPE
            DESCRIPTION.
        stepNum : TYPE
            DESCRIPTION.

        Returns
        -------
        mass : TYPE
            DESCRIPTION.
        cost : TYPE
            DESCRIPTION.

        """
        
        # Determine the production step
        prodStep = comp.productionSteps[stepNum]
        
        # Determine the material type, name and data
        matType = prodStep.materials
        
        if matType == 'resin':
            # Areal weight calculation is for fabric
            matType = 'fabric'
            
            # Determine resin data
            resinType = 'resin'
            resinName = comp.matDetails[resinType]
            resinDatabase = materialVars[resinType][resinName]
        
        materialName = comp.matDetails[matType]
        matDatabase = materialVars[matType][materialName]
        
        # Determine the scaling variables
        scalingVar = prodStep.materialScaling[0]
        
        # Creating a list of either: (i) surface area and areal weight, or (ii)
        # surface area, density and thickness, to calculate the part mass for 
        # this production step
        scalingList1 = [comp.scaleVars[scalingVar]]
        scalingList2 = [self.MatCheck(matDatabase[val], val) for val in prodStep.materialScaling[1:]]
        scalingList = scalingList1 + scalingList2
        
        # Determine the mass of materials by multiplying each value in the list
        mass = 1.0
        for n in scalingList:
            mass *= n
        
        # Check for resin and hardener
        try:
            if resinType == 'resin':
                # Mass calculation provides the fabric mass, convert to resin mass
                fwf = matDatabase['fibre content']
                resinMixMass = mass*(1 - fwf)/(fwf)
                
                try:
                    # If a hardener is included determine proportion of hardener mass and cost
                    resinHardenerRatio = resinDatabase['resin-hardener ratio']
                    hardenerName = comp.matDetails['hardener']
                
                    mass = resinMixMass*(resinHardenerRatio)/(resinHardenerRatio+1.0)
                
                    hardenerMass = mass/resinHardenerRatio
                    
                    comp.materials.mass['hardener'] = hardenerMass
                    unitCost = materialVars['hardener'][hardenerName]['cost']
                    
                    hardenerCost = hardenerMass*unitCost
                    
                    comp.materials.matCost['hardener'] = hardenerCost
                    
                    # Determine scrap mass and costs for the hardener
                    scrappage = prodStep.scrapRate
                    
                    if scrappage is not None:
                        scrapMass = (scrappage/(1-scrappage))*hardenerMass
                        comp.materials.massScrap['hardener'] = scrapMass
                        
                        scrapCost = scrapMass*unitCost
                        comp.materials.matCostScrap['hardener'] = scrapCost
                    
                except ValueError:
                    
                    mass = resinMixMass
                
        except:
            pass
        
        # Determine the unit cost of materials
        try:
            if resinType == 'resin':
                unitCost = resinDatabase['cost']
                matType = resinType
            
        except:
            unitCost = matDatabase['cost']
        
        # Save the mass of materials
        comp.materials.mass[matType] += mass
        
        # Save the cost of materials
        cost = mass*unitCost
        comp.materials.matCost[matType] += cost
        
        # Determine scrap mass and costs for the material
        scrappage = prodStep.scrapRate
        
        if scrappage is not None:
            scrapMass = (scrappage/(1-scrappage))*mass
            comp.materials.massScrap[matType] += scrapMass
            
            scrapCost = scrapMass*unitCost
            comp.materials.matCostScrap[matType] += scrapCost
            
        
        return mass, cost


    def ConsumablesCost(self, comp, materialVars, stepNum):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.
        materialVars : TYPE
            DESCRIPTION.
        stepNum : TYPE
            DESCRIPTION.

        Returns
        -------
        stepConsCost : TYPE
            DESCRIPTION.

        """
        
        # Determine the production step
        prodStep = comp.productionSteps[stepNum]
        
        # Add the consumables to the part object
        consList = prodStep.consumables
        comp.consumables.MaterialAdd(consList)
        
        stepConsCost = 0.0
        
        # Determine the costs for each consumable type
        for consName in consList:
            
            # Determine the consumable data
            consDatabase = materialVars['consumables'][consName]
            
            # Determine the scaling variables
            consScaling = consDatabase['scaling variable']
            
            scalingList1 = [comp.scaleVars[consScaling]]
            scalingList2 = [self.MatCheck(consDatabase['areal weight'], 'areal weight')]
            scalingList = scalingList1 + scalingList2
            
            # Determine the mass of the consumable
            mass = 1.0
            for n in scalingList:
                mass *= n
            
            comp.consumables.mass[consName] += mass
            
            # Determine the cost of the consumable
            unitCost = consDatabase['cost']
            
            consCost = mass*unitCost
            comp.consumables.matCost[consName] += consCost
            
            # Determine the mass and cost of scrap consumable materials
            scrappage = consDatabase['scrap_rate']
            
            scrapMass = (scrappage/(1-scrappage))*mass
            comp.consumables.massScrap[consName] = scrapMass
            
            scrapCost = scrapMass*unitCost
            comp.consumables.matCostScrap[consName] = scrapCost
            
            stepConsCost += consCost + scrapCost
        
        return stepConsCost
    
    
    def LabourCost(self, comp, materialVars, productionVars, stepNum):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.
        materialVars : TYPE
            DESCRIPTION.
        productionVars : TYPE
            DESCRIPTION.
        stepNum : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        # Determine the production step
        prodStep = comp.productionSteps[stepNum]
        
        if prodStep.labourScaling is not None:
            
            scalingVar = prodStep.labourScaling[0]
            
            # Determine if any scaling variables are applicable to the step
            labScale = prodStep.labourScaling[1]
            
            productionType = comp.productionNames[stepNum]
            # print(productionType, labScale, productionVars[productionType], '\n', productionVars)
            rateCoef, rateExp = productionVars[productionType][labScale]['value']
            
            staffNum = prodStep.staff
            
            labourHours = rateCoef * (comp.scaleVars[scalingVar])**rateExp
            
            processHours = labourHours / staffNum
            
            cost = labourHours * productionVars['General']['salary']['value']
        
        elif type(prodStep.labourHours) is float:
            
            staffNum = prodStep.staff
            
            labourHours = prodStep.labourHours
            
            processHours = labourHours / staffNum
            
            cost = labourHours * productionVars['General']['salary']['value']
            
        else:
            
            if 'Cure' in prodStep.name:
                
                if 'resin' in comp.matDetails.keys():
                    matType = 'resin'
                    
                elif 'prepreg' in comp.matDetails.keys():
                    matType = 'prepreg'
                
                cycleType = 'cure cycle'
                
            elif 'bondline' in prodStep.name:
                
                matType = 'adhesive'
                
                cycleType = 'cure cycle'
                
            elif 'Post-cure' in prodStep.name:
                
                if 'resin' in comp.matDetails.keys():
                    matType = 'resin'
                    
                elif 'prepreg' in comp.matDetails.keys():
                    matType = 'prepreg'
                    
                cycleType = 'post cure cycle'
            
            matName = comp.matDetails[matType]
            
            cureFile = materialVars[matType][matName][cycleType]
            
            typeVal = 'float, float, float'
            columns = [0,1,2]
            
            cureCycleVals = array([loadtxt(self.directory+self.dirInputDatabases+self.CSVloc+cureFile, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)])
            
            processHours = sum(cureCycleVals[0,1])
            
            staffNum = prodStep.staff
            
            labourHours = processHours * staffNum
            
            cost = labourHours * productionVars['General']['salary']['value']
        
        comp.labour.labourHours[stepNum] = labourHours
        comp.labour.processHours[stepNum] = processHours
        comp.labour.labourCosts[stepNum] = cost
        
        return cost, labourHours, processHours
        
    
    def LabourActivity(self, comp):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        for i, stepName in enumerate(comp.productionSteps):
            activityName = stepName.activity
            comp.labour.activityCosts[activityName] += comp.labour.labourCosts[i]   
            comp.labour.activityHours[activityName] += comp.labour.labourHours[i] 
        
        
    def CommonEquipment(self, partsList):
        """
        

        Returns
        -------
        None.

        """
        
        if len(self.commonEquipment.keys()) == 0:
            # List of single "factory level" equipment
            commonEquipmentList = ['Freezer', 'NDT equipment',
                                   'Ply cutter', 'Oven', 'Autoclave']
            
            # Distribute the part costs by manufacturing category among the parts
            self.commonCount = dict(zip(commonEquipmentList,[0 for i in range(len(commonEquipmentList))]))
            
            # Loop through all parts and count the times the common equipment are used
            for compList in partsList:
                
                for comp in compList:
                            
                    for item in comp.equipment.equipmentCosts.keys():
                        
                        if item in commonEquipmentList:
                            
                            self.commonCount[item] += 1
            
            self.commonEquipment = {key: val for key, val in self.commonCount.items() if val > 0.0}
            
            self.commonEquipmentCost = {key: 0.0 for key, val in self.commonEquipment.items()}

    
    def MouldsCost(self, comp, mouldType):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.
        mouldType : TYPE
            DESCRIPTION.

        Returns
        -------
        partMouldCost : TYPE
            DESCRIPTION.

        """
        
        equipVariables = self.equipmentVars['tooling_and_moulds'][mouldType]
        
        [scalingCoef, scalingConstant] = equipVariables['scaling values']
        
        scalingName = equipVariables['scaling variables']
        
        lifetime = float(equipVariables['lifetime'])
        
        scaleVar = comp.scaleVars[scalingName]
        
        totalMouldCost = scalingCoef * scaleVar + scalingConstant
        
        partMouldCost = totalMouldCost / lifetime
        
        return partMouldCost
    
    
    def ProductionLines(self, productLines, productionVars, lineType):
        """
        

        Parameters
        ----------
        productLines : TYPE
            DESCRIPTION.
        productionVars : TYPE
            DESCRIPTION.
        lineType : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        # Flatten parts list and retrieve the process hours for each component
        flatList = [val for partsList1 in self.partsList for val in partsList1 if val.brand == lineType]
        
        productLineTimes = array([val.labour.totalProcessHours for val in flatList])
        
        # The general production variables
        ppa = productionVars['General']['ppa']['value']
        productHours = productionVars['General']['productHours']['value']
        productDays = productionVars['General']['productDays']['value']
        
        # Determine the number of available production hours per year
        annualHours = productHours * productDays
        
        # Determine the total process hours needed to meet production quotas
        totalPLtimes = productLineTimes*ppa
        
        # Determine the number of production lines for each preform
        numProductLines = ceil(totalPLtimes / annualHours)
        
        # Save the rounded up number of production lines for each preform
        for i, lineVal in enumerate(numProductLines):
            productLines[flatList[i].name] = lineVal
    
        
    def EquipmentCost(self, comp, stepNum):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.
        stepNum : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # Determine the number of parts produced per year
        partsPerAnnum = self.productionVars['General']['ppa']['value']
        
        equipList = comp.productionSteps[stepNum].capitalEquipment
        
        for equipVal in equipList:
            
            # Check for a mould in the list
            if("mould" in equipVal.lower()):
                
                # Determine the cost of the mould per part
                partMouldCost = self.MouldsCost(comp, equipVal)
                
                # Save the equipment cost per part
                cost = partMouldCost
                
            else:
                
                # Calculate the annual depreciation of each piece of equipment
                annualDepr = self.DepreciationCost(equipVal)
                
                # Determine the portion of annual equipment cost incldued in each part
                if equipVal not in list(self.commonEquipment.keys()):
                    if 'assembly' in comp.brand:
                        numProductionLines = self.assemblyLines[comp.name]
                    else:
                        numProductionLines = self.productLines[comp.name]
                else:
                    numProductionLines = 1.0
                
                # Save the equipment cost per part
                cost = annualDepr * numProductionLines / partsPerAnnum
            
#            self.PowerCost(comp, equipVal, processTime)
            
            
            if equipVal not in list(self.commonEquipment.keys()):
                comp.equipment.equipmentCosts[equipVal] = cost
            else:
                self.commonEquipmentCost[equipVal] = cost
          
            
    def PowerCost(self, comp, equipVal, processTime):
        """
        

        Parameters
        ----------
        comp : TYPE
            DESCRIPTION.
        equipVal : TYPE
            DESCRIPTION.
        processTime : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        powerUsage = self.equipmentVars['capital_equipment'][equipVal]['average power usage']
        
        energyRate = self.productionVars['General']['energy']['value']
        
        comp.equipment.powerCosts[equipVal] = processTime * powerUsage * energyRate
    
    
    def OverheadCost(self, totalCost, overheadCost):
        """
        

        Parameters
        ----------
        totalCost : TYPE
            DESCRIPTION.
        overheadCost : TYPE
            DESCRIPTION.

        Returns
        -------
        overheadCosts : TYPE
            DESCRIPTION.

        """
        
        overheadCosts = totalCost * 0.05
        
        return overheadCosts
        
    
    def TotalCosts(self):
        """
        

        Returns
        -------
        None.

        """
        
        flatList = [val for partsList1 in self.partsList for val in partsList1]
        
        ## Breakdown of the cost centres
        # Structure mass and cost
        self.breakdown_material_mass_struct = {}
        self.breakdown_material_cost_struct = {}
        
        # Scrap mass and cost
        self.breakdown_material_mass_scrap = {}
        self.breakdown_material_cost_scrap = {}
        
        # Consumables mass and cost
        self.breakdown_consumables_mass = {}
        self.breakdown_consumables_cost = {}
        
        # Labour hours and cost 
        self.breakdown_labour_hours = {}
        self.breakdown_labour_cost = {}
        
        # Equipment costs
        self.breakdown_equipment_cost = {}
        self.breakdown_equipment_item_cost = {}
        
        for mat in self.materialVars['consumables'].keys():
            # Consumables mass and cost values
            self.breakdown_consumables_mass[mat] = 0.0
            self.breakdown_consumables_cost[mat] = 0.0
            
        for act in self.activityLevels:
            # Labour hours and cost values
            self.breakdown_labour_hours[act] = 0.0
            self.breakdown_labour_cost[act] = 0.0
            
        for val in flatList:
            for matVal in val.matDetails.values():
                # Structure mass and cost values
                self.breakdown_material_mass_struct[matVal] = 0.0
                self.breakdown_material_cost_struct[matVal] = 0.0
                
                # Scrap mass and cost values
                self.breakdown_material_mass_scrap[matVal] = 0.0
                self.breakdown_material_cost_scrap[matVal] = 0.0
        
        for val in flatList:
            # Material costs
            for mat in val.materials.matCost.keys():
                matName = val.matDetails[mat]
                # Structure mass and cost values
                self.breakdown_material_mass_struct[matName] += val.materials.mass[mat]
                self.breakdown_material_cost_struct[matName] += val.materials.matCost[mat]
                
                # Scrap mass and cost values
                self.breakdown_material_mass_scrap[matName] += val.materials.massScrap[mat]
                self.breakdown_material_cost_scrap[matName] += val.materials.matCostScrap[mat]
            
            # Consumables costs
            for mat in val.consumables.matCost.keys():
                # Consumables mass and cost values
                self.breakdown_consumables_mass[mat] += val.consumables.mass[mat] + val.consumables.massScrap[mat]
                self.breakdown_consumables_cost[mat] += val.consumables.matCost[mat] + val.consumables.matCostScrap[mat]
        
            # Labour costs
            for act in self.activityLevels:
                # Labour hours and cost values
                self.breakdown_labour_cost[act] += val.labour.activityCosts[act]
                self.breakdown_labour_hours[act] += val.labour.activityHours[act]
            
            # Equipment costs
            self.breakdown_equipment_cost[val.name] = val.equipment.cost
        
        # Equipment cost values
        self.breakdown_equipment_cost['factory'] = sum(self.commonEquipmentCost.values())
        
        for val in flatList:
            for equip in val.equipment.equipmentCosts.keys():
                # Equipment cost values
                try:
                    self.breakdown_equipment_item_cost[equip] += val.equipment.equipmentCosts[equip]
                except:
                    self.breakdown_equipment_item_cost[equip] = val.equipment.equipmentCosts[equip]
    
        for equip in self.commonEquipmentCost.keys():
            # Equipment cost values
            try:
                self.breakdown_equipment_item_cost[equip] += self.commonEquipmentCost[equip]
            except:
                self.breakdown_equipment_item_cost[equip] = self.commonEquipmentCost[equip]
                
        # Get list of material categories
        materialList = []
        self.breakdown_material_categories = {}
        
        for material in self.materialVars.items():
            for matKey in material[1]:
                
                if matKey in self.breakdown_material_cost_struct.keys():
                    
                    materialList.append(material[0])
                    
        materialList = list(set(materialList))
        
        if sum(self.breakdown_consumables_cost.values()) > 0.0:
            materialList.append('consumables')
        
        for mat in materialList:
            self.breakdown_material_categories[mat] = 0.0
        
        for matName in materialList:
            for partSet in self.partsList:
                for part in partSet:
                    try:
                        self.breakdown_material_categories[matName] += part.materials.matCost[matName] + part.materials.matCostScrap[matName]
                    except:
                        pass
        
        # Total cost of the wing
        totalMaterialsCosts = sum([costVal.materials.cost for costVal in flatList])
        
        self.costs_consumables = sum([costVal.consumables.cost for costVal in flatList])
        
        self.costs_materials = totalMaterialsCosts + self.costs_consumables
        
        self.costs_labour = sum([sum(costVal.labour.labourCosts) for costVal in flatList])
        
        partEquipmentCosts = sum([costVal.equipment.cost for costVal in flatList])
        
        factoryEquipmentCosts = sum(self.commonEquipmentCost.values())
        
        self.costs_equipment = partEquipmentCosts + factoryEquipmentCosts
        
        self.costs_manufacturing = self.costs_materials + self.costs_labour + self.costs_equipment
        
        self.costs_overheads = self.OverheadCost(self.costs_manufacturing, self.costs_overheads)
        
        self.costs_manufacturing += self.costs_overheads
        
        self.structure_mass = sum([val.materials.TotalMass(structureMass=True) for val in flatList])
        
        self.unit_cost = self.costs_manufacturing / self.structure_mass
        
        return self.costs_manufacturing
        