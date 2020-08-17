"""
Wing Composites Manufacturing Cost Model

Author: Edward M Fagan

"""

import os
from numpy import loadtxt, ceil
import copy
from MapParametersIn import readInputs
from MapParametersOut import writeOutputs, sumMats, sumTotals


class component:
    
    def __init__(self, partName, partType, matDetails=None, partBrand='preform', activityLevels=['Manufacturing']):
        # General object variables
        self.name = partName
        self.type = partType
        self.brand = partBrand
        
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
        
        
        
    # Method for resetting dictionaries to zeros or for setting up a new empty dictionary
    def emptyDict(self, dictVars, newDict={}):
        
        for val in iter(dictVars):
            newDict[val] = 0.0
            
        return newDict
    
    # Method to populate a list of production steps
    def productStepDef(self, productionDict, append=True):
        
        if append is False:
            self.productionSteps = []
        
        # Create a list of production steps
        for label in productionDict:
            
            stepInstance = ProductionStep()
            stepInstance.stepLabel = label
            
            for stepVar in productionDict[label]:
                
                try:
                    # Check if the member exists
                    getattr(stepInstance, stepVar)
                    
                    # If data exist for the member in the input database add them
                    if productionDict[label][stepVar] != 'None':
                        setattr(stepInstance, stepVar, productionDict[label][stepVar])
                        
                except AttributeError:
                    pass
                    
            self.productionSteps.append(stepInstance)
        
        # Populate the list of equipment for the production steps
        self.equipment.findEquipment(self.productionSteps)
    
    def productionDef(self, inputParams, productionMethods):
        
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
                    
                    self.productStepDef(activitySteps, append=False)
                    self.productionNames = self.productionNames + [activityName for i in range(len(activitySteps))]
                    
            except:
                pass
            
        
    "Internal class for material cost related functions and variables"
    class Materials:
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
                    self.dictionaryFill(matDetails)
                
                elif type(matDetails) is str or list:
                    self.materialAddition(matDetails)
        
        # Method for populating a dictionary with zeros
        def materialDict(self, matDict, matDetails):
            
            for val in iter(matDetails):
                matDict[val] = 0.0
                
        # Method for populating all dictionaries with zeros and adding new elements
        def dictionaryFill(self, matDetails):
            for obj in [self.mass, self.matCost, self.massScrap, self.matCostScrap]:
                self.materialDict(obj, matDetails)
        
        # Method for adding a new material or list of materials
        def materialAddition(self, materials):
            materialDict = {}
            
            # Check for single item or list for addition
            if type(materials) is str:
                materials = [materials]
            
            # Create dummy dictionary
            for mats in materials:
                materialDict[mats] = 'N/A'
            
            self.dictionaryFill(materialDict)
        
        # Method for summing up the total mass
        def totalMass(self, structureMass=False):
            if structureMass is False:
                self.materialMass = sum(self.mass.values()) + sum(self.massScrap.values())
            elif structureMass is True:
                return sum(self.mass.values())
        
        # Method for summing up the total costs
        def totalCost(self):
            self.cost = sum(self.matCost.values()) + sum(self.matCostScrap.values())
        
    "Internal class for labour cost related functions and variables"
    class Labour:
        def __init__(self, numSteps=None):
            # Make these into dictionaries to capture the values for each step
            if numSteps is None:
                self.processHours = []
                self.labourHours = []
                self.labourCosts = []
            else:
                self.processHours = self.fillEmpty(numSteps)
                self.labourHours = self.fillEmpty(numSteps)
                self.labourCosts = self.fillEmpty(numSteps)
            
        # Method to populate the dictionaries
        def fillEmpty(self, numSteps):
            return [0.0 for i in range(numSteps)]
            
        # Method for summing up the results
        def totals(self):
            self.totalProcessHours = sum(self.processHours)
            self.totalLabourHours = sum(self.labourHours)
            self.totalCost = sum(self.labourCosts)
    
    "Internal class for equipment cost related functions and variables"
    class Equipment:
        def __init__(self, activityLevels):
            # Make these into dictionaries to capture the values for each step
            self.equipmentList = {}
            self.equipmentCosts = {}
            self.activityCosts = {}
            
            self.activityDict(activityLevels, self.equipmentList)
            self.activityDict(activityLevels, self.activityCosts)
            
            self.cost = 0.0
            
        def activityDict(self, activityLevels, equipDict):
            for act in activityLevels:
                equipDict[act] = []
            
        # A method to populate the dictionaries
        def findEquipment(self, productionSteps):
            
            try:
                fullList = [val.capitalEquipment for val in iter(productionSteps)]
                activityList = [val.activity for val in iter(productionSteps)]
                
                for i, activity in enumerate(activityList):
                    if fullList[i][0] != 'None':
                        self.equipmentList[activity] += fullList[i]
                        
                        for equip in fullList[i]:
                            if equip != 'None':
                                self.equipmentCosts[equip] = 0.0
            
            except:
                pass
        
        # Method for summing up the total costs
        def totals(self):
            self.cost = sum(self.equipmentCosts.values())


class ProductionStep:
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


class CompManuCost:
    
    def __init__(self, directory, csvFileRange, inputFile=''):
        """ 
        Import the material, production and construction parameters
        """
        self.directory = directory
        self.CSVloc = "\\CSV Files\\"
        self.extraCSV = "Input Range\\"+csvFileRange+"\\"
        dirInputDatabases = "\\Input Databases\\"
        dirOutputDatabases = "\\Output Databases\\"
        
        try:
            os.mkdir(directory+dirOutputDatabases+csvFileRange)
        except FileExistsError:
            pass
        
        # Import the various input databases
        if len(inputFile) == 0:
            # Default manufacturing inputs database name
            inputFile = "AP4inputVars"
        
        AP4inputVars = dirInputDatabases + inputFile + ".xml"
        consVariables = dirInputDatabases + "constructionVariablesDatabase.xml"
        productionVariables = dirInputDatabases + "productionVariablesDatabase.xml"
        productionMethods = dirInputDatabases + "productionMethodsDatabase.xml"
        materialVariables = dirInputDatabases + "materialsDatabase.xml"
        equipmentVariables = dirInputDatabases + "equipmentVariablesDatabase.xml"

        AP4inputVars = self.directory + AP4inputVars
        consVariables = self.directory + consVariables
        productionVariables = self.directory + productionVariables
        productionMethods = self.directory + productionMethods
        materialVariables = self.directory + materialVariables
        equipmentVariables = self.directory + equipmentVariables
        
        self.ap4Params, self.consInputVars, self.productionVars, self.productionMethods, self.materialVars, self.equipmentVars = readInputs(AP4inputVars, consVariables, productionVariables, productionMethods, materialVariables, equipmentVariables)
        
        self.equipmentList = {}
        
        # Set the construction variables
        self.numSpars = int(float(self.ap4Params['spar']['# spars']))
        self.numWebs = int(float(self.ap4Params['web']['# webs']))
        self.numSkins = int(float(self.ap4Params['skin']['# skins']))
        
        # Add the material names to the part thickness csv file names
        if(self.ap4Params['spar']['fabric'] != 'N/A'):
            sparMatName = self.ap4Params['spar']['fabric']
        else:
            sparMatName = self.ap4Params['spar']['prepreg']
        
        if(self.ap4Params['web']['fabric'] != 'N/A'):
            webMatName = self.ap4Params['web']['fabric']
        else:
            webMatName = self.ap4Params['web']['prepreg']
            
        if(self.ap4Params['skin']['fabric'] != 'N/A'):
            skinMatName = self.ap4Params['skin']['fabric']
        else:
            skinMatName = self.ap4Params['skin']['prepreg']
        
        self.consInputVars['internal_structure']['sparThick'] = sparMatName + "_" + self.consInputVars['internal_structure']['sparThick']
        self.consInputVars['internal_structure']['webThick'] = webMatName + "_" + self.consInputVars['internal_structure']['webThick']
        self.consInputVars['internal_structure']['skinThick'] = skinMatName + "_" + self.consInputVars['internal_structure']['skinThick']
        
        """
        New:
            Set up dictionaries for all the parts in the assembly
            Assign the appropriate materials to each part
        """
        self.activityLevels = ['preform', 'cure', 'assembly', 'finishing']
        
        self.brandTypes = {'spar': 'preform', 'web': 'preform', 'skin': 'preform', 'wing': 'assembly'}
        
#        self.spars = [component("spar"+str(i+1), "spar", matDetails=self.materialDetails(self.ap4Params, "spar"), activityLevels=self.activityLevels) for i in range(self.numSpars)]
#        self.webs = [component("web"+str(i+1), "web", matDetails=self.materialDetails(self.ap4Params, "web"), activityLevels=self.activityLevels) for i in range(self.numWebs)]
#        self.skins = [component("skin"+str(i+1), "skin", matDetails=self.materialDetails(self.ap4Params, "skin"), activityLevels=self.activityLevels) for i in range(self.numSkins)]
#        self.wing = [component("wing", "wing", matDetails=self.materialDetails(self.ap4Params, "wing"), partBrand='assembly', activityLevels=self.activityLevels)]
#        
        self.spars = self.setComponents(self.ap4Params, self.activityLevels, 'spar', self.brandTypes['spar'], self.ap4Params['spar']['# '+'spar'+'s'])
        self.webs = self.setComponents(self.ap4Params, self.activityLevels, 'web', self.brandTypes['web'], self.ap4Params['web']['# '+'web'+'s'])
        self.skins = self.setComponents(self.ap4Params, self.activityLevels, 'skin', self.brandTypes['skin'], self.ap4Params['skin']['# '+'skin'+'s'])
        self.wing = self.setComponents(self.ap4Params, self.activityLevels, 'wing', self.brandTypes['wing'], self.ap4Params['wing']['# '+'wing'+'s'])
        
        # Leaving it like this until differentiating them becomes necessary
        self.skins[0].side = 'Lower'
        self.skins[1].side = 'Upper'
        self.webs[0].side = 'Fore'
        
        self.partsList = [self.spars, self.webs, self.skins, self.wing]
        
        self.productLines = {}
        self.assemblyLines = {}
        
        self.commonEquipment = {}
        
        self.manufacturingCosts = 0.0
        self.materialCosts = 0.0
        self.labourCosts = 0.0
        self.equipmentCosts = 0.0
        
        self.structureMass = 0.0
        self.unitCost = 0.0
    
    
    def reSetManufacturing(self):
        self.reSetComponents(self.spars, self.ap4Params, self.activityLevels)
        self.reSetComponents(self.webs, self.ap4Params, self.activityLevels)
        self.reSetComponents(self.skins, self.ap4Params, self.activityLevels)
        self.reSetComponents(self.wing, self.ap4Params, self.activityLevels)

        self.skins[0].side = 'Lower'
        self.skins[1].side = 'Upper'
        self.webs[0].side = 'Fore'
        
        self.productLines = {}
        self.assemblyLines = {}
        
        self.commonEquipment = {}
        
        self.manufacturingCosts = 0.0
        self.materialCosts = 0.0
        self.labourCosts = 0.0
        self.equipmentCosts = 0.0
        
        self.structureMass = 0.0
        self.unitCost = 0.0
        
    
    def setComponents(self, ap4Params, activityLevels, partName, brand, numParts):
        return [component(partName+str(i+1), partName, matDetails=self.materialDetails(ap4Params, partName), partBrand=brand, activityLevels=activityLevels) for i in range(numParts)]
    
    def reSetComponents(self, compList, ap4Params, activityLevels):
        for comp in compList:
            scalingVars = copy.deepcopy(comp.scaleVars)
            comp.__init__(comp.name, comp.type, self.materialDetails(ap4Params, comp.type), partBrand=self.brandTypes[comp.type], activityLevels=activityLevels)
            comp.scaleVars = copy.deepcopy(scalingVars)
        
    # Create a dictionary of the materials and material categories for a part
    def materialDetails(self, ap4Params, partType):
        materialCategories = ['fabric', 'resin', 'hardener', 'prepreg', 'core', 'adhesive', 'coating']
        materialDetails = {}
        
        for val in ap4Params[partType]:
            if val in materialCategories:
                if ap4Params[partType][val] != 'N/A':
                    materialDetails[val] = ap4Params[partType][val]
        
        return materialDetails
    

    def scale(self):
        direct = self.directory + self.CSVloc + self.extraCSV
        
        for compList in [self.spars, self.webs, self.skins]:
            for comp in compList:
                newScalingVariables(comp, direct, self.consInputVars, self.materialVars)
    
        assemblyScaling(self.skins, self.webs, self.wing[0])
    
    
    """ 
    Calculates the annual portion of depreciation for a piece of equipment
    """
    def Depr(self, equipName):
        equipVariables = self.equipmentVars['capital_equipment'][equipName]
        
        purchaseVal = equipVariables['purchase cost']
        installFactor = equipVariables['installation cost']/100.0 + 1.0
        usefulLife = equipVariables['useful life']
        salvageVal = equipVariables['salvage value']
        
        annualDepr = (purchaseVal*installFactor - salvageVal)/usefulLife
        
        return annualDepr
    
    """ 
    Calculates the portion of mould set costs for each part
    """

    
    """ 
    Calculates the equipment costs and building costs for the wing
    """

    """ 
    Calculates the number of production lines
    """

    """ 
    Calculates the building costs
    """
    def buildCost(self, equipName, partName):
#        equipName = "Balancing equipment and scales"
#        partName = 'spar1'
        
        equipVariables = comp1.equipmentVars['capital_equipment'][equipName]
        
        if(equipVariables['floorspace'] == "N/A"):
            floorArea = 0.0
            
        elif(equipVariables['floorspace'] == "calculation"):
            length = equipVariables['machine length']
            width = equipVariables['machine width']
            floorArea = length*width
            
        elif(equipVariables['floorspace'] == "Surface Area"):
            if('wing' in partName):
                floorArea = comp1.scalingVars[partName][partName]['Surface Area']
            else:
                partType = partName[:-1]
                floorArea = comp1.scalingVars[partType][partName]['Surface Area']
            
        elif(equipVariables['floorspace'] == "wingLen"):
            length = comp1.consInputVars['external_geometry']['wingLen']
            width = 2.5
            floorArea = length*width
            
        return floorArea
    
    
    def productionRun(self, scaling=True, reSet=False):
        
        if reSet is True:
            self.reSetManufacturing()
        
        if scaling is True:
            self.scale()
        
        for compList in self.partsList:
            
            for comp in compList:
                
                comp.productionDef(self.ap4Params, self.productionMethods)
                
                self.partRun(comp, self.materialVars, self.productionVars, runEquip=False)
            
        self.determineManufLines()
            
        self.determineCommonEquip()
        
        for compList in self.partsList:
            
            for comp in compList:
            
                self.partRun(comp, self.materialVars, self.productionVars, runMats=False, runLab=False)
        
        self.totalCosts()
        
        
    def partRun(self, comp, materialVars, productionVars, runMats=True, runLab=True, runEquip=True):
        
        if runMats is True:
            self.materialsRun(comp, materialVars)
        
        if runLab is True:
            self.labourRun(comp, materialVars, productionVars)
        
        if runEquip is True:
            # All the labour calculations have to be done before the number of manufacturing
            # lines and hence equipment costs can be determined
            try:
                self.equipmentRun(comp)
            except:
                print('No production line data available')
                pass
        
        
    def materialsRun(self, comp, materialVars):
        
        productSteps = comp.productionSteps
        
        # Run through steps in production
        for i, step in enumerate(productSteps):
            
            # Determine material costs
            if step.materials is not None:
                
                self.materialCost(comp, materialVars, i)
            
            # Determine consumables costs
            if step.consumables[0] != 'None':
                
                self.consumablesCost(comp, materialVars, i)
                
        comp.materials.totalCost()
        comp.materials.totalMass()
        comp.consumables.totalCost()
    
    
    def labourRun(self, comp, materialVars, productionVars):
        
        productSteps = comp.productionSteps
        
        comp.labour = comp.Labour(len(productSteps))
        
        # Run through steps in production
        for i, step in enumerate(productSteps):
            
            # Determine labour costs
            self.labourCost(comp, materialVars, productionVars, i)
            
        comp.labour.totals()
    
    
    def equipmentRun(self, comp):
        
        productSteps = comp.productionSteps
        
        # Run through steps in production
        for i, step in enumerate(productSteps):
            
            # Determine the equipment costs
            if step.capitalEquipment[0] != 'None':
                
                self.equipCost(comp, i)
                
        comp.equipment.totals()
    
    """
    New material cost methods
    """
    def matValProcess(self, value, variableName):
        
        if variableName == 'density':
            value = value
        else:
            value = value/1000.0
            
        return value
    
    
    def materialCost(self, comp, materialVars, stepNum):
        
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
        
        scalingList1 = [comp.scaleVars[scalingVar]]
        scalingList2 = [self.matValProcess(matDatabase[val], val) for val in prodStep.materialScaling[1:]]
        scalingList = scalingList1 + scalingList2
        
        # Determine the mass of materials
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


    def consumablesCost(self, comp, materialVars, stepNum):
        
        # Determine the production step
        prodStep = comp.productionSteps[stepNum]
        
        # Add the consumables to the part object
        consList = prodStep.consumables
        comp.consumables.materialAddition(consList)
        
        stepConsCost = 0.0
        
        # Determine the costs for each consumable type
        for consName in consList:
            
            # Determine the consumable data
            consDatabase = materialVars['consumables'][consName]
            
            # Determine the scaling variables
            consScaling = consDatabase['scaling variable']
            
            scalingList1 = [comp.scaleVars[consScaling]]
            scalingList2 = [self.matValProcess(consDatabase['areal weight'], 'areal weight')]
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
    
    
    def labourCost(self, comp, materialVars, productionVars, stepNum):
        
        # Determine the production step
        prodStep = comp.productionSteps[stepNum]
        
        if prodStep.labourScaling[0] != 'None':
            
            scalingVar = prodStep.labourScaling[0]
            
            # Determine if any scaling variables are applicable to the step
            labScale = prodStep.labourScaling[1]
            
            productionType = comp.productionNames[stepNum]
            
            rateCoef, rateExp = productionVars[productionType][labScale]
            
            staffNum = prodStep.staff
            
            labourHours = rateCoef * (comp.scaleVars[scalingVar])**rateExp
            
            processHours = labourHours / staffNum
            
            cost = labourHours * productionVars['General']['salary'][0]
        
        elif type(prodStep.labourHours) is float:
            
            staffNum = prodStep.staff
            
            labourHours = prodStep.labourHours
            
            processHours = labourHours / staffNum
            
            cost = labourHours * productionVars['General']['salary'][0]
            
        else:
#            productionType = comp.productionNames[stepNum]
            
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
            
            cureCycleVals = array([loadtxt(self.directory+self.CSVloc+self.extraCSV+cureFile, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)])
            
            processHours = sum(cureCycleVals[0,1])
            
            staffNum = prodStep.staff
            
            labourHours = processHours * staffNum
            
            cost = labourHours * productionVars['General']['salary'][0]
        
        comp.labour.labourHours[stepNum] = labourHours
        comp.labour.processHours[stepNum] = processHours
        comp.labour.labourCosts[stepNum] = cost
        
        
        
#        if('ATL' in labourVars[1] or 'AFP' in labourVars[1]):
#            productRate = self.productionVars[productionMethod][labourVars[1]][0] * (self.scalingVars[compType][compName][labourVars[0]])**(self.productionVars[productionMethod][labourVars[1]][1])
#            processHours = productRate * (compDict['Materials']['Mass']['prepreg'] + compDict['Materials']['Mass Scrap']['prepreg'])
#            labourHours = processHours * staffNum
        
    def determineCommonEquip(self):
        
        if len(self.commonEquipment.keys()) == 0:
            self.commonEquip(self.partsList)
    
    
    def commonEquip(self, partsList):
        
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
        
    
    def mouldCost(self, comp, mouldType):
        
        equipVariables = self.equipmentVars['tooling_and_moulds'][mouldType]
        
        [scalingCoef, scalingConstant] = [float(x) for x in str.split(equipVariables['scaling values'], ',')]
        
        scalingName = equipVariables['scaling variables']
        
        lifetime = float(equipVariables['lifetime'])
        
        scaleVar = comp.scaleVars[scalingName]
        
        totalMouldCost = scalingCoef * scaleVar + scalingConstant
        
        partMouldCost = totalMouldCost / lifetime
        
        return partMouldCost
    
    
    def determineManufLines(self):
        
        if len(self.productLines.keys()) == 0:
            self.productionLineAnalysis(self.productLines, self.productionVars, lineType='preform')
        
        if len(self.assemblyLines.keys()) == 0:
            self.productionLineAnalysis(self.assemblyLines, self.productionVars, lineType='assembly')
        
    
    def productionLineAnalysis(self, productLines, productionVars, lineType):
        
        # Flatten parts list and retrieve the process hours for each component
        flatList = [val for partsList1 in self.partsList for val in partsList1 if val.brand == lineType]
        
        productLineTimes = array([val.labour.totalProcessHours for val in flatList])
        
        # The general production variables
        ppa = productionVars['General']['ppa'][0]
        productHours = productionVars['General']['productHours'][0]
        productDays = productionVars['General']['productDays'][0]
        
        # Determine the number of available production hours per year
        annualHours = productHours * productDays
        
        # Determine the total process hours needed to meet production quotas
        totalPLtimes = productLineTimes*ppa
        
        # Determine the number of production lines for each preform
        numProductLines = ceil(totalPLtimes / annualHours)
        
        # Save the rounded up number of production lines for each preform
        for i, lineVal in enumerate(numProductLines):
            productLines[flatList[i].name] = lineVal
    
        
    def equipCost(self, comp, stepNum):
        # Determine the number of parts produced per year
        partsPerAnnum = self.productionVars['General']['ppa'][0]
        
        equipList = comp.productionSteps[stepNum].capitalEquipment
        
        for equipVal in equipList:
            
            # Check for a mould in the list
            if("mould" in equipVal):
                
                # Determine the cost of the mould per part
                partMouldCost = self.mouldCost(comp, equipVal)
                
                # Save the equipment cost per part
                cost = partMouldCost
                
            else:
                
                # Calculate the annual depreciation of each piece of equipment
                annualDepr = self.Depr(equipVal)
                
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
            
            
            if equipVal not in list(self.commonEquipment.keys()):
                comp.equipment.equipmentCosts[equipVal] = cost
            else:
                self.commonEquipmentCost[equipVal] = cost
                

    
    def totalCosts(self):
        # Total cost of the wing
        flatList = [val for partsList1 in self.partsList for val in partsList1]
        
        totalMaterialsCosts = sum([costVal.materials.cost for costVal in flatList])
        
        totalConsumablesCosts = sum([costVal.consumables.cost for costVal in flatList])
        
        self.materialCosts = totalMaterialsCosts + totalConsumablesCosts
        
        self.labourCosts = sum([sum(costVal.labour.labourCosts) for costVal in flatList])
        
        partEquipmentCosts = sum([costVal.equipment.cost for costVal in flatList])
        
        factoryEquipmentCosts = sum(self.commonEquipmentCost.values())
        
        self.equipmentCosts = partEquipmentCosts + factoryEquipmentCosts
        
        self.manufacturingCosts = self.materialCosts + self.labourCosts + self.equipmentCosts
        
        self.structureMass = sum([val.materials.totalMass(structureMass=True) for val in flatList])
        
        self.unitCost = self.manufacturingCosts / self.structureMass
        

