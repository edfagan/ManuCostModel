"""
Created on Thu Jul 23 11:29:29 2020

Author: Edward M Fagan

"""

from numpy import array, loadtxt, transpose, zeros, full, ceil, where, sqrt

"""
Spars structural breakdown
"""
def SparStructuralBreakdown(direct, chordName, sparWidthName, sparThickName, wingSpan, plyWidth):
#     Inputs
    typeVal = 'float'
    columns = (0)
    
    chordDist = loadtxt(direct+chordName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)
    
    # Need to decide on keeping SparLocation file setup or changing to a spar width
    sparWidthArray = transpose(array([loadtxt(direct+sparWidthName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
    
    sparPlyNums = transpose(array([loadtxt(direct+sparThickName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
    
#     Processes
    seg = len(chordDist)
    
    segLen = wingSpan/float(seg)
    
    segments = full((seg,1), segLen)
    
    sparSA = segments*sparWidthArray
    
    cutPliesByWidth = ceil(sparWidthArray/plyWidth)
#    print("seg: ", segments, "spar", sparWidthArray, "sparply", sparPlyNums)
    totalSurfArea = segments*sparWidthArray*sparPlyNums
    totalPlyLength = segments*sparPlyNums*cutPliesByWidth
    
#     Outputs:
#       Values required for mass calculation: totalSurfArea
#       Values required for labour calculation: sparSA, totalPlyLength
    
    outputs = [sum(sparSA)[0], sum(totalSurfArea)[0], sum(totalPlyLength)[0]]
    outputs = [float(val) for val in outputs]
    outputNames = ['Surface Area', 'Ply Surface Area', 'Ply Length']
    
    return outputs, outputNames

"""
Skins structural breakdown
"""
def SkinStructuralBreakdown(direct, chordName, airfoilName, sparWidthName, skinThickName, wingSpan, plyWidth, skinType, webLocsName, coreCheck=0, coreVals=None):
    
    def distCalc(coord1, coord2):
        return sqrt((coord2[0] - coord1[0])**2.0 + (coord2[1] - coord1[1])**2.0)
        
#    Inputs
    typeVal = 'float'
    columns = (0)
    
    chordDist = loadtxt(direct+chordName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)
    
    seg = len(chordDist)
    
    typeVal = 'str'
    columns = (0)
    
#    chordName = "Chord.csv"
#    direct = r'C:\Users\0116092S\Dropbox\SFI Industry Fellowship\08 - Tasks & Tools\01 Work Package 1\02 Engineering Analysis\Python Cost Model\Verification\CSV Files\\'
#    airfoilName = "Airfoils Distribution.csv"
#    seg = 124
#    skinType = 'LP'
    
    airfoilsDist = loadtxt(direct+airfoilName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)
    
    lengthDist = zeros((seg,1))
    LElengthDist = zeros((seg,1))
    TElengthDist = zeros((seg,1))
    
    for spanLoc in range(len(chordDist)):
        
        airfoilSect = "Airfoils_" + airfoilsDist[spanLoc] + ".csv"
        typeVal = 'float,float'
        columns = (0,1)
        airfoils = loadtxt(direct+airfoilSect, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)
        
        # Find the point where the coordinates switch from pressure side to suction side
        switch = where(airfoils[0] == 0.0)
        point = list(switch)[0][-1]
        
        if(skinType == 'Lower'):
            skinSide = [airfoils[0][:point], airfoils[1][:point]]
            
            # Find the point where the spar cap begins
            typeVal = 'float'
            columns = (0)
            webLocation = loadtxt(direct+webLocsName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)
            
            # Find the airfoil coordinate where the spar cap begins
            switch2 = where(airfoils[0] <= webLocation[spanLoc])
#            point2 = list(switch2)[0][-1] + 1
            point2 = len(where(array(switch2)<point)[0])
            LEskinSide = [airfoils[0][:point2], airfoils[1][:point2]]
            
        else:
            skinSide = [airfoils[0][point:], airfoils[1][point:]]
            
            # Find the point where the spar cap begins
            typeVal = 'float'
            columns = (0)
            webLocation = loadtxt(direct+webLocsName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)
            
            # Find the point where the spar cap begins
            switch2 = where(airfoils[0][point:] <= webLocation[spanLoc])
            point2 = list(switch2)[0][-1] + 1
            LEskinSide = [airfoils[0][point:point+point2], airfoils[1][point:point+point2]]
        
        surfaceLength = sum([distCalc([skinSide[0][i], skinSide[1][i]], [skinSide[0][i+1], skinSide[1][i+1]]) for i in range(len(skinSide[0])-1)])
        LEsurfaceLength = sum([distCalc( [LEskinSide[0][i], LEskinSide[1][i]] , [LEskinSide[0][i+1], LEskinSide[1][i+1]] ) for i in range(len(LEskinSide[0])-1)])
        
        lengthDist[spanLoc] = surfaceLength*chordDist[spanLoc]
        LElengthDist[spanLoc] = LEsurfaceLength*chordDist[spanLoc]
    
    typeVal = 'float'
    columns = (0)
    
    sparWidthArray = transpose(array([loadtxt(direct+sparWidthName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
    
    skinPlyNums = transpose(array([loadtxt(direct+skinThickName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
    
#     Processes
    segLen = wingSpan/float(seg)
    segments = full((seg,1), segLen)
    
    skinSA = segments*lengthDist
    
    cutPliesByWidth = ceil(lengthDist/plyWidth)
    
    totalSurfArea = segments*lengthDist*skinPlyNums
    totalPlyLength = segments*skinPlyNums*cutPliesByWidth
    
    # Sweep, twist and LE-offset (in z-direction) and chord also factor in bond length
    # update once data is available
    bondLine = segments*2
    
    """
    Core structural breakdown
    """
    if(coreCheck == 0):
        # Outputs:
        outputs = [sum(skinSA)[0], sum(totalPlyLength)[0], sum(totalSurfArea)[0], sum(bondLine)[0], 0.0, 0.0, 0.0]
        outputs = [float(val) for val in outputs]
    
    else:
        # Skin core breakdown
        # Inputs
        coreWidth, coreThick, coreFrac = coreVals
        
        # Determine spanwise distribution of the core thickness
        typeVal = 'float'
        columns = (1)
        LEcoreThickDist = transpose(array([loadtxt(direct+skinThickName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
        
        columns = (2)
        TEcoreThickDist = transpose(array([loadtxt(direct+skinThickName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
        
        # Check if there's a fraction of the panel without core material
        if('N/A' in coreFrac):
            coreFracDist = zeros((seg,1))
        else:
            columns = (0)
            coreFracDist = transpose(array([loadtxt(direct+coreFrac, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
        
        # Calculate the length of the trailing edge panel region
        TElengthDist = lengthDist - sparWidthArray - LElengthDist 
        
        # Processes
        LEcorePlyNums = ceil(LEcoreThickDist/coreThick)
        TEcorePlyNums = ceil(TEcoreThickDist/coreThick)
        
        # Next lines are wrong, since the length of the fore and aft sections is 
        # dependent on the location of the spars and those values are not known yet
        LEskinCoreLength = LElengthDist - coreFracDist
        TEskinCoreLength = TElengthDist - coreFracDist
        
        LEskinCoreSA = segments*LEskinCoreLength
        TEskinCoreSA = segments*TEskinCoreLength
        
        skinCoreSA = TEskinCoreSA + LEskinCoreSA
        
        LEcoreCutPliesByWidth = ceil(LEskinCoreLength/(coreWidth))
        TEcoreCutPliesByWidth = ceil(TEskinCoreLength/(coreWidth))
        
        LEcoreTotalSurfArea = segments*LEskinCoreLength*LEcorePlyNums
        LEcoreTotalPlyLength = segments*LEcorePlyNums*LEcoreCutPliesByWidth
        
        TEcoreTotalSurfArea = segments*TEskinCoreLength*TEcorePlyNums
        TEcoreTotalPlyLength = segments*TEcorePlyNums*TEcoreCutPliesByWidth
        
        coreTotalSurfArea = TEcoreTotalSurfArea + LEcoreTotalSurfArea
        coreTotalPlyLength = TEcoreTotalPlyLength + LEcoreTotalPlyLength
#        Outputs:
#           Values required for mass calculation: totalSurfArea, coreTotalSurfArea
#           Values required for labour calculation: skinSA, skinCoreSA, totalPlyLength, coreTotalPlyLength
        outputs = [sum(skinSA)[0], sum(totalPlyLength)[0], sum(totalSurfArea)[0], sum(bondLine)[0], sum(skinCoreSA)[0], sum(coreTotalPlyLength)[0], sum(coreTotalSurfArea)[0]]
        outputs = [float(val) for val in outputs]
    
    outputNames = ['Surface Area', 'Ply Length', 'Ply Surface Area', 'Bondline', 'Core Surface Area', 'Core Ply Length', 'Core Ply Surface Area']
    
    return outputs, outputNames


"""
Webs structural breakdown
"""
def WebStructuralBreakdown(direct, chordName, wingSpan, webThickName, skinThickName, sparThickName, sparWidthName, skinPlyThick, plyWidth, sparPlyThick, webLocsName, airfoilName, webType, coreCheck=0, coreVals=None):
    
    def distCalc(coord1, coord2):
        return sqrt((coord2[0] - coord1[0])**2.0 + (coord2[1] - coord1[1])**2.0)
#    Inputs
    # Profile thickness should be based on location of the web in the profile
    # update once data is available
    typeVal = 'float'
    columns = (0)
    
    chordDist = loadtxt(direct+chordName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)
    
    webPlyNums = transpose(array([loadtxt(direct+webThickName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
    
    skinPlyNums = transpose(array([loadtxt(direct+skinThickName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
    
    sparPlyNums = transpose(array([loadtxt(direct+sparThickName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
    
    sparWidthArray = transpose(array([loadtxt(direct+sparWidthName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
    
    chordDist = transpose(array([chordDist]))
    
#    Processes
    seg = len(chordDist)
    
    segLen = wingSpan/float(seg)
    segments = full((seg,1), segLen)
    
    typeVal = 'str'
    columns = (0)
    
    airfoilsDist = loadtxt(direct+airfoilName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)
    
    profileThickDist = zeros((seg,1))
    webHeight = zeros((seg,1))
    
    typeVal = 'float'
    columns = (0)
    webLocation = loadtxt(direct+webLocsName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)
    
    for spanLoc in range(len(chordDist)):
#    for spanLoc in range(10):
        
        airfoilSect = "Airfoils_" + airfoilsDist[spanLoc] + ".csv"
        typeVal = 'float,float'
        columns = (0,1)
        airfoils = loadtxt(direct+airfoilSect, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)
        
        # Find the point where the coordinates switch from pressure side to suction side
        switch = where(airfoils[0] == 0.0)
        point = list(switch)[0][-1]
    
    
        # Find the point where the spar cap begins
        try: # Check in case the web location is zero, i.e. no web
            if(webType == 'Fore'):
                webPoint = webLocation[spanLoc]
            elif(webType == 'Aft'):
                webPoint = webLocation[spanLoc] + sparWidthArray[spanLoc]/chordDist[spanLoc]
            
            # Find the airfoil coordinate where the spar cap begins on HP skin
            switch2 = where(airfoils[0] <= webPoint)
            point2 = len(where(array(switch2)<point)[0])
            skinSideLower = [airfoils[0][:point2], airfoils[1][:point2]]
            
            # Find the point where the spar cap begins on the LP skin
            switch2 = where(airfoils[0][point:] <= webPoint)
            point2 = list(switch2)[0][-1] + 1
            skinSideUpper = [airfoils[0][point:point+point2], airfoils[1][point:point+point2]]
            
            # Determine the height of the web
            webDist = distCalc( [skinSideLower[0][-1], skinSideLower[1][-1]] , [skinSideUpper[0][-1], skinSideUpper[1][-1]] )
            
            profileThickDist[spanLoc] = webDist*chordDist[spanLoc]
            
            webHeight[spanLoc] = profileThickDist[spanLoc] - 2*skinPlyNums[spanLoc]*skinPlyThick - 2*sparPlyNums[spanLoc]*sparPlyThick
            
        except IndexError:
            profileThickDist[spanLoc] = 0.0
            
            webHeight[spanLoc] = 0.0
    
    
#    webHeight = profileThickDist - 2*skinPlyNums*skinPlyThick - 2*sparPlyNums*sparPlyThick
    
    webSA = segments*webHeight
    
    pliesByWidth = ceil(webHeight/plyWidth)
    
    totalSurfArea = segments*webHeight*webPlyNums
    totalPlyLength = segments*webPlyNums*pliesByWidth
    
    # Sweep, twist, LE-offset (in z-direction) and chord also factor in bond length
    # update once data is available
    bondLine = segments*2
    
    """
    Core structural breakdown
    """
    if(coreCheck == 0):
        # Outputs:
        outputs = [sum(webSA)[0], sum(totalPlyLength)[0], sum(totalSurfArea)[0], sum(bondLine)[0]]
        outputs = [float(val) for val in outputs]
        
    else:
        # Web core breakdown
        # Inputs
        coreFrac, coreThick, coreWidth = coreVals
        
        typeVal = 'float'
        columns = (1)
        coreThickDist = transpose(array([loadtxt(direct+webThickName, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
        
        if('N/A' in coreFrac):
            coreFracDist = zeros((seg,1))
        else:
            columns = (0)
            coreFracDist = transpose(array([loadtxt(direct+coreFrac, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)]))
            
        # Processes
        webCorePlyNums = coreThickDist/coreThick
        
        # Calculate the height of the web where core is present
        webCoreHeight = zeros((seg,1))
        
        for spanLoc in range(len(webHeight)):
            if(webHeight[spanLoc] == 0.0):
                webCoreHeight[spanLoc] = 0.0
            else:
                webCoreHeight[spanLoc] = webHeight[spanLoc] - coreFracDist[spanLoc]
        
        webCoreSA = segments*webCoreHeight
        
        corePliesByWidth = ceil(webCoreHeight/coreWidth)
        
        coreTotalSurfArea = segments*webCoreHeight*webCorePlyNums
        coreTotalPlyLength = segments*webCorePlyNums*corePliesByWidth
        
        # Outputs:
        outputs = [sum(webSA)[0], sum(totalPlyLength)[0], sum(totalSurfArea)[0], sum(bondLine)[0], sum(webCoreSA)[0], sum(coreTotalPlyLength)[0], sum(coreTotalSurfArea)[0]]
        outputs = [float(val) for val in outputs]
        
    outputNames = ['Surface Area', 'Ply Length', 'Ply Surface Area', 'Bondline', 'Core Surface Area', 'Core Ply Length', 'Core Ply Surface Area']
    
    return outputs, outputNames


# Determine the scaling variables
def ScalingVariables(comp, direct, consInputVars, materialVars):
    """ 
    Determine the scaling variables for material, labour and equipment costs
    Call the individual structural breakdown modules for each of the parts
    """
    
    wingSpan = float(consInputVars['external_geometry']['wingLen'])
    chordName = consInputVars['external_geometry']['chordDist']
    sparWidthName = consInputVars['internal_structure']['sparLocDist']
    sparThickName = consInputVars['internal_structure']['sparThick']
    skinThickName = consInputVars['internal_structure']['skinThick']
    webThickName = consInputVars['internal_structure']['webThick']
    webLocsName = consInputVars['internal_structure']['webLocDist']
    airfoilName = consInputVars['external_geometry']['airfoils']
    
    if comp.type == 'spar':
        # Determine the scaling variables for the spar
        
        # Check for fabric or prepreg for reinforcement
        try:
            sparMatName = comp.matDetails['fabric']
            matType = 'fabric'
        except KeyError:
            sparMatName = comp.matDetails['prepreg']
            matType = 'prepreg'
            
        # Determine material properties
        sparPlyWidth = float(materialVars[matType][sparMatName]['width'])/1000.0
        sparPlyThick = float(materialVars[matType][sparMatName]['thickness (cured)'])/1000.0
        
        # Determine the scaling variables for the spar
        scalingValues, scalingNames = SparStructuralBreakdown(direct, chordName, sparWidthName, sparThickName, wingSpan, sparPlyWidth)
        
        scalingValues.append(consInputVars['external_geometry']['wingLen'])
        scalingNames.append('Part Length')
    
    elif comp.type == 'skin':
        # Determine the scaling variables for the skin
        
        # Check for fabric or prepreg for reinforcement
        try:
            skinMatName = comp.matDetails['fabric']
            matType = 'fabric'
        except KeyError:
            skinMatName = comp.matDetails['prepreg']
            matType = 'prepreg'
            
        # Determine material properties
        skinPlyWidth = float(materialVars[matType][skinMatName]['width'])/1000.0
        skinPlyThick = float(materialVars[matType][skinMatName]['thickness (cured)'])/1000.0
    
        skinType = comp.side
        
        try:
            # Check for core material in the skin laminate
            comp.matDetails['core']
            
            SkinCoreCheck = 1
            
            # Determine core material variables
            skinCoreName = comp.matDetails['core']
            coreWidth = float(materialVars['core'][skinCoreName]['width'])/1000.0
            coreThick = float(materialVars['core'][skinCoreName]['thickness'])
            coreFrac = consInputVars['internal_structure']['skinPanelFraction']
            
            skinCoreVals = coreWidth, coreThick, coreFrac
            
        except KeyError:
            
            SkinCoreCheck = 0
            
            skinCoreVals = None
        
        # Determine the scaling variables for the skin
        scalingValues, scalingNames = SkinStructuralBreakdown(direct, chordName, airfoilName, sparWidthName, skinThickName, wingSpan, skinPlyWidth, skinType, webLocsName, SkinCoreCheck, skinCoreVals)
        
        scalingValues.append(consInputVars['external_geometry']['wingLen'])
        scalingNames.append('Part Length')
        
    elif comp.type == 'web':
        # Determine the scaling variables for the web
        
        # Check for fabric or prepreg for reinforcement in the web
        try:
            webMatName = comp.matDetails['fabric']
            matType = 'fabric'
        except KeyError:
            webMatName = comp.matDetails['prepreg']
            matType = 'prepreg'
        
        webPlyWidth = float(materialVars[matType][webMatName]['width'])/1000.0
        webType = comp.side
        
        # Check for fabric or prepreg for reinforcement in the skins
        skinMatName = skinThickName.split('_SkinThickness.csv')[0]
            
        try:
            materialVars['prepreg'][skinMatName]
            matType = 'prepreg'
        except:
            try:
                materialVars['fabric'][skinMatName]
                matType = 'fabric'
            except:
                pass
            
        skinPlyThick = float(materialVars[matType][skinMatName]['thickness (cured)'])/1000.0
        
        # Check for fabric or prepreg for reinforcement in the spars
        sparMatName = sparThickName.split('_SparThickness.csv')[0]
            
        try:
            materialVars['prepreg'][sparMatName]
            matType = 'prepreg'
        except:
            try:
                materialVars['fabric'][sparMatName]
                matType = 'fabric'
            except:
                pass
        
        sparPlyThick = float(materialVars[matType][sparMatName]['thickness (cured)'])/1000.0
        
        try:
            # Check for core material in the web laminate
            comp.matDetails['core']
            
            CoreCheck = 1
            
            # Determine core material variables
            webCoreName = comp.matDetails['core']
            coreWidth = float(materialVars['core'][webCoreName]['width'])/1000.0
            coreThick = float(materialVars['core'][webCoreName]['thickness'])
            coreFrac = consInputVars['internal_structure']['webPanelFraction']
            
            coreVals = coreFrac, coreThick, coreWidth
            
        except KeyError:
            
            SkinCoreCheck = 0
            
            coreVals = None
        
        # Determine the scaling variables for the skin
        scalingValues, scalingNames = WebStructuralBreakdown(direct, chordName, wingSpan, webThickName, skinThickName, sparThickName, sparWidthName, skinPlyThick, webPlyWidth, sparPlyThick, webLocsName, airfoilName, webType, CoreCheck, coreVals)
        
        scalingValues.append(consInputVars['external_geometry']['wingLen'])
        scalingNames.append('Part Length')
        
    # Assign the scaling variables
    for i, var in enumerate(scalingNames):
        comp.scaleVars[var] = scalingValues[i]
        
        
def AssemblyScaling(skins, webs, wing):
    
    # Determine the scaling variables for the wing
    wingSA = sum([val.scaleVars['Surface Area'] for val in skins])
    shellBond = sum([val.scaleVars['Bondline'] for val in skins])
    webBond = sum([val.scaleVars['Bondline'] for val in webs])
    webNum = float(len(webs))
    
    scalingValues = [wingSA, webBond, shellBond, shellBond/2.0, webNum]
    scalingNames = ['Surface Area', 'webs_Bondline', 'shells_Bondline', 'shell_Bondline', '# webs']
    
    # Assign the scaling variables
    for i, var in enumerate(scalingNames):
        wing.scaleVars[var] = scalingValues[i]
    
