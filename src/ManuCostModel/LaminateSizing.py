# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 11:32:40 2020

@author: 0116092S
"""

from numpy import array, savetxt, loadtxt, transpose, floor, average, ones, zeros, full, arange, ceil, pi, where, arcsin, sqrt
from matplotlib.pyplot import plot, figure, quiver, gca, boxplot, subplots, show
import matplotlib.pyplot as plt
import os

"""
Layup definitions analysis
"""

    
""" Define the functions for the analysis """
# Local chord formula Eq3.4 from 4D197 "P4-E30-TN-Analytical Mass Upscale Model"
def chordForm(y, wingSpan, wingArea):
    
    # Find chord at root (Eq3.6 from 4D197)
    chordRoot = 4*wingArea/pi/wingSpan
    
    # Local chord length
    chord = chordRoot*(1.0 - (y/(wingSpan/2.0))**2.0)**0.5
    
    return chord

# Local bending moment formula Eq3.16 from 4D197 "P4-E30-TN-Analytical Mass Upscale Model"
def Mx(y, wingSpan, tetherTens):
    
    # Find the lift force (Eq2.3 from "Analytical Mass Upscale Model" 4D197 (first printout))
    Ly = 4*tetherTens/pi/wingSpan
    
    y = abs(y)
    
    # Local bending moment
    M = Ly*(1./3.*(wingSpan/2.0)**2.0*(1.0 - (y/(wingSpan/2.0))**2.0)**(3.0/2.0) - y*(wingSpan/4.0)*(pi/2.0 - arcsin(y/(wingSpan/2.0)) - (y/(wingSpan/2.0))*(1.0 - (y/(wingSpan/2.0))**2.0)**0.5 ) )
    
    return M

# Local shear force formula Eq3.22 from 4D197 "P4-E30-TN-Analytical Mass Upscale Model"
def Fy(y, wingSpan, tetherTens):
    
    # Find the lift force (Eq2.3 from "Analytical Mass Upscale Model" 4D197 (first printout))
    Ly = 4*tetherTens/pi/wingSpan
    
    y = abs(y)
    
    # Local shear force
    Fy = Ly*(wingSpan/4.0)*( pi/2.0 - ( arcsin(y/(wingSpan/2.0)) + (y/(wingSpan/2.0))*(1.0 - (y/(wingSpan/2.0))**2.0 )**0.5 ) )
    
    return Fy

# Local torsion formula Eq3.34 from 4D197 "P4-E30-TN-Analytical Mass Upscale Model"
def My(y, V, Cm, wingArea, wingSpan, tetherTens, rho):
    
    y = abs(y)
    
    Mval = 0.5*rho*Cm*(wingArea**2.0)/(pi*wingSpan)*(V**2.0)*( pi/2.0 - ( arcsin(y/(wingSpan/2.0)) + (y/(wingSpan/2.0))*(1.0 - (y/(wingSpan/2.0))**2.0 )**0.5 ) )

    return abs(Mval)

# Local spar cap thickness and mass
def sparThickCalc(sigmaMax, SF, t, c, M, sparWidth, segment, matDens=0.0, returnMass=False):
    
    # Local cross-sectional area formula Eq3.13 from 4D197 "P4-E30-TN-Analytical Mass Upscale Model"
    if(c == 0.0):
        S = 0.0
    else:
        S = (SF)/(sigmaMax*t)*(M/c)
    
    if(returnMass == False):
        # Individual spar cap thickness
        sparThick = S/sparWidth
        
        return sparThick
    else:        
        # Spar cap mass for the local segment for one spar cap
        localMass = S*segment*matDens
        return localMass

# Local shear web thickness and mass
def shearThickCalc(tauMax, SF, Fy, t, c, segment, matDens=0.0, returnMass=False):
    
    # Local cross-sectional area formula Eq3.23 from 4D197 "P4-E30-TN-Analytical Mass Upscale Model"
    S = SF/(tauMax)*(Fy)
    
    # Shear web thickness
    if(c == 0.0):
        shearThick = 0.0
    else:
        shearThick = S/(t*c)
    
    if(returnMass == False):
        return shearThick
    else:
        # Shear web mass for the local segment
        localMass = S*segment*matDens
        return localMass

# Local skin thickness Eq3.35 from 4D197 "P4-E30-TN-Analytical Mass Upscale Model
def skinThickCalc(tauMax, SF, MyLoc, gamma, c, segment, matDens=0.0, returnMass=False):
    
    if(c == 0.0):
        skinThick = 0.0
        S = 0
    else:
        # Formula for skin thickness  (Eq3.35)
        skinThick = SF/tauMax*pi/(2*gamma**2.0)*MyLoc/(c**2.0)
        # Eq3.37
        S = SF/(tauMax)*(pi/(a*(1+t)))*MyLoc/c
        
    if(returnMass == False):
        return skinThick
    else:
        # Shear web mass for the local segment
        localMass = S*segment*matDens
        return localMass
    
# Calculate the mass of each part
def arrayMasses(skinPlyNums, skinPly, a, c, cLoc, t, segment, densSkin, sparPlyNums, sparPly, sparWidth, densUD, shearPlyNums, shearPly, densShear):
        # Determine skins mass (top and bottom skins)    
        skinsArray = array(skinPlyNums)*skinPly*(2*a*array(c)*(1+t))*segment*densSkin
        # Determine the spars mass (top and bottom spars)
        sparsArray = array(sparPlyNums)*sparPly*sparWidth*segment*densUD*2.0
        # Determine the web mass (single web design)
        websArray = array(shearPlyNums)*shearPly*(array(c)*t)*segment*densShear
        
        return skinsArray, sparsArray, websArray

# 
def spanRange(wingSpan, segments):
    
    segment = int(wingSpan/segments)
    
    start = -int(wingSpan/2)
    end = int(wingSpan/2) + int(segment)
    
    return [y for y in range(start,end,segment)]
    
# 
def chordRange(wingSpan, wingArea, segments, chordRatio_Main=1.0):
    
    # The chord length distribution of the wing
    y_range = spanRange(wingSpan, segments)
#    c_range = [chordForm(y, wingSpan, wingArea) for y in y_range]
    cLoc_range = [chordForm(y, wingSpan, wingArea)*chordRatio_Main for y in y_range]
    
    return cLoc_range
    
    
# 
def sparDistribution(wingSpan, tetherTens, wingArea, aspectRatio, segments, chordRatio_Main, t, sparInputs):
    
    segment = int(wingSpan/segments)
    
    y_range = spanRange(wingSpan, segments)
    
    cLoc_range = chordRange(wingSpan, wingArea, segments, chordRatio_Main)
    
    sigmaMax, sigmaSF, sparWidth, sparPly, densUD = sparInputs
    
    """ Determine the individual spar cap ply thickness distribution """
    # The bending moment distribution of the wing
    M_dist = [Mx(y, wingSpan, tetherTens) for y in y_range]
    
    # The spar cap thickness distribution
    sparThickDist = [sparThickCalc(sigmaMax, sigmaSF, t, cLoc_range[i], M_dist[i], sparWidth, segment) for i in range(len(y_range))]
    
    # The number of spar cap plies along the wing
    sparPlyNums = [ceil(max(sparThickDist[i+1], sparThickDist[i], 2.0*sparPly)/sparPly/2.0) for i in range(len(y_range)-1)]
    
    # The spar cap mass distribution
    sparMassDist = [sparThickCalc(sigmaMax, sigmaSF, t, cLoc_range[i], M_dist[i], sparWidth, segment, matDens=densUD, returnMass=True) for i in range(len(y_range))]
    
    sparMassSummed = sum(sparMassDist)
    
    # Eq3.17 Mass of the spar caps (new version May 2020)
    m_caps = 0.25*(densUD*sigmaSF)/(sigmaMax*t)*(16.0/18.0 - pi/4.0)*tetherTens*wingSpan*aspectRatio
    
    return sparPlyNums, sparMassSummed, m_caps

# 
def webDistribution():
    """ Determine the single shear web ply thickness distribution """
    # The shear force distribution of the wing
    Fy_dist = [Fy(y, wingSpan, tetherTens) for y in y_range]
    
    # The shear web thickness distribution
    shearThickDist = [shearThickCalc(tauMaxShear, tauShearSF, Fy_dist[i], t, cLoc_range[i], segment) for i in range(len(y_range))]
    
    # The number of shear web plies along the wing
    shearPlyNums = [ceil(max(shearThickDist[i+1], shearThickDist[i], 2.0*shearPly)/shearPly) for i in range(len(y_range)-1)]
    
    # The shear web mass distribution
    shearMassDist = [shearThickCalc(tauMaxShear, tauShearSF, Fy_dist[i], t, cLoc_range[i], segment, matDens=densShear, returnMass=True) for i in range(len(y_range))]
    
    shearMassSummed = sum(shearMassDist)
    
    # Eq3.25 Mass of the shear web
    m_web = (2./3.)*(densShear*tauShearSF)/(tauMaxShear*pi)*tetherTens*wingSpan
    
#        # Wolfram alpha => integral (rho*S/tau)*((4T/(pi*b))*(b/4)*((pi/2) - (asin(x/(b/2)) + (x/(b/2))*(1 - (x/b/2)^2)^0.5))) from 0 to b/2
#        m_webNew = (15.0*sqrt(15.0) - 52.0)*tauShearSF*densShear*wingSpan*tetherTens/(24*pi*tauMaxShear)
    
# 
def skinDistribution():
    """ Determine the skin ply thickness distribution """
    # The shear force distribution of the wing
    My_dist = [My(y, V, Cm, wingArea, wingSpan, tetherTens, rho) for y in y_range]
    
    # The shear web thickness distribution
    skinThickDist = [skinThickCalc(tauMaxSkin, tauSkinSF, My_dist[i], gamma, c_range[i], segment) for i in range(len(y_range))]
    
    # The number of shear web plies along the wing
    skinPlyNums = [ceil(max(skinThickDist[i+1], skinThickDist[i], 2.0*skinPly)/skinPly) for i in range(len(y_range)-1)]
    
    # The shear web mass distribution
    skinMassDist = [skinThickCalc(tauMaxSkin, tauSkinSF, My_dist[i], gamma, c_range[i], segment, matDens=densShear, returnMass=True) for i in range(len(y_range))]
    
    skinMassSummed = sum(skinMassDist)
    
    # Skin mass Eq3.39 (old version pre-May 2020)
#        m_skin = densSkin*tauSkinSF/tauMaxSkin*(2.0 * pi**2.0)/(a*(1.0 + t))*0.5*rho*average(c_range)*Cm*(V**2.0)*((wingSpan/4.0)**2.0)*((pi/2.0)**2.0 - 1.0)
    
    # Skin mass Eq3.38 (new version May 2020)
    m_skin = densSkin*tauSkinSF/tauMaxSkin*(pi)/(2.0*a*(1.0 + t))*0.5*rho*wingArea*Cm*(V**2.0)*(wingSpan/4.0)*((pi/2.0)**2.0 - 1.0)
    
    




if(__name__ == '__main__'):
    
    """ Begin the analysis """
    # Read in the input mass table
    directory = r"C:\Users\0116092S\Documents\GitHub\Composite-Cost-Model\CSV Files"
    inputFile = "\Mass Inputs.csv"
    typeVal = 'float, float, float, float, float, float'
    columns = [0,1,2,3,4,5]
    massInputs = array([loadtxt(directory+inputFile, dtype=typeVal, delimiter=',', skiprows=1, usecols=columns, unpack=True)])
    
    # Set the output variable
    massOutputs = zeros([6,len(massInputs[0][0])])
    
    # Define constants for the analysis  
    # Note: All units in mm, N and MPa
    
    # Profile thickness percentage
    t = 0.21
    
    # Predefined spar cap width
    sparWidth = 450.0
    """
    # Cost Analysis Inputs
#    # UD spar cap material: AS4/8552 UD
#    sigmaMax = 1800
#    sigmaSF = 4.14
#    densUD = 1.59/1000000.0 # kg/mm3
#    arealUD = 190.0 # Fibres aerial weight
#    sparPly = 0.188
#
#    # MD shear webs material: AS4/8552 PW 
#    tauMaxShear = 84.0
#    tauShearSF = 2.79
#    densShear = 1.57/1000000.0 # kg/mm3
#    arealShear = 193.0 # Fibres aerial weight
#    shearPly = 0.198
#
#    # MD skin material: 6781 S2/5320-1 
#    tauMaxSkin = 54.0
#    tauSkinSF = 1.77
#    densSkin = 1.78/1000000.0 # kg/mm3
#    arealSkin = 300.0 # Fibres aerial weight
#    skinPly = 0.2616
    """
    
    """
    Shortlist Analysis Inputs
    """
    # UD spar cap material: UD150 Fabric
#    UDname = "UD150 Fabric"
#    sigmaMax = 784.0   # UCS
#    sigmaSF = 4.14
#    densUD = 1.48/1000000.0 # kg/mm3
#    sparPly = 0.20
    
#    # UD spar cap material: UD150 Prepreg
#    UDname = "UD150 Prepreg"
#    sigmaMax = 980.0   # UCS
#    sigmaSF = 4.14
#    densUD = 1.528/1000000.0 # kg/mm3
#    sparPly = 0.18
#    
#    # UD spar cap material: ATL Tape/AFP Tows
    UDname = "ATL Tape"
#    UDname = "AFP Tows"
    sigmaMax = 1903.0   # UCS
    sigmaSF = 4.14
    densUD = 1.573/1000000.0 # kg/mm3
    sparPly = 0.262
    
#    # BIAX shear webs material: Zoltek BIAX fabric
    ShearName = "Zoltek BIAX Fabric"
    tauMaxShear = 47.2
    tauShearSF = 2.79
    densShear = 1.449/1000000.0 # kg/mm3
    shearPly = 0.46
    
#    # BIAX skin material: Zoltek BIAX fabric
    SkinName = "Zoltek BIAX Fabric"
    tauMaxSkin = 47.2
    tauSkinSF = 1.77
    densSkin = 1.449/1000000.0 # kg/mm3
    skinPly = 0.46
    
#    # BIAX shear webs material: Zoltek BIAX prepreg
#    ShearName = "Zoltek BIAX Prepreg"
#    tauMaxShear = 59.0
#    tauShearSF = 2.79
#    densShear = 1.449/1000000.0 # kg/mm3
#    shearPly = 0.46
    
#    # BIAX skin material: Zoltek BIAX prepreg
#    SkinName = "Zoltek BIAX Prepreg"
#    tauMaxSkin = 59.0
#    tauSkinSF = 1.77
#    densSkin = 1.449/1000000.0 # kg/mm3
#    skinPly = 0.46
#    
    # BIAX shear webs material: ATL Tape/AFP Tows
#    ShearName = "ATL BIAX Tape"
##    ShearName = "AFP BIAX Tows"
#    tauMaxShear = 60.0
#    tauShearSF = 2.79
#    densShear = 1.573/1000000.0 # kg/mm3
#    shearPly = 0.262*2.0
    
    # Biax skin material: ATL Tape/AFP Tows
#    SkinName = "ATL BIAX Tape"
##    SkinName = "AFP BIAX Tows"
#    tauMaxSkin = 60.0
#    tauSkinSF = 1.77
#    densSkin = 1.573/1000000.0 # kg/mm3
#    skinPly = 0.262*2.0
    
    
    # Ratio of each wing element (2 element profile)
    chordRatio_Main = 0.787
    chordRatio_Flap = 0.3074
    
    # Aerodynamic input variables
    rho = 1.2/1000/1000/1000 # kg/mm3
    V = 35.0*1000 # Peak 80 m/s
    Cm = 0.008793   # 0.25
    
    # Geometrical constants for the wing skin
    a = 0.7
    gamma = a*(1 + t)
    
    # Reference Layups worksheet in Input Data workbook for design definitions
#    # Design 1
#    sparPly = 0.15 # Fibre Glast 2114
#    shearPly = 1.04 # F-1833
#    skinPly = 0.13 # F-2402
    
#    # Design 2
#    sparPly = 0.15 # HR40 Prepreg
#    shearPly = 0.48 # Hexcel Prepreg
#    skinPly = 0.48 # Hexcel Prepreg
#    
#    # Design 3
#    sparPly = 1.02 # F-2286
#    shearPly = 1.04 # F-1833
#    skinPly = 0.13 # F-2402
#    
#    # Design 4
#    sparPly = 0.15 # HR40 Prepreg
#    shearPly = 1.04 # F-1833
#    skinPly = 0.13 # F-2402
    
    """ Determine the three thickness distributions """
#    for i in range(len(massInputs[0][0])):
    for i in range(19,20):
        
#        tetherTens = massInputs[0][5,i]
#        wingArea = massInputs[0][0,i]
        
        tetherTens = 700.0
        wingArea = 85.0
#        tetherTens = 298.67
#        wingArea = 70.0
        
        segments = 40
        aspectRatio = 12.5
        tetherTens = tetherTens*1000.0
        wingArea = wingArea*1000000.0
        wingSpan = sqrt(wingArea*aspectRatio)
        
        wingSpan = floor(wingSpan/1000)*1000
        
        # Define the segments of the wing
        segment = int(wingSpan/segments)
        
        start = -int(wingSpan/2)
        end = int(wingSpan/2) + int(segment)
        
        y_range = [y for y in range(start,end,segment)]
        
        # The chord length distribution of the wing
        c_range = [chordForm(y, wingSpan, wingArea) for y in y_range]
        cLoc_range = [chordForm(y, wingSpan, wingArea)*chordRatio_Main for y in y_range]
        
#         The width of the spar caps
#        sparWidth = 4*wingArea/pi/wingSpan*0.15
#        
#         The thickness of the core material
#        coreThick = round((0.0725*wingArea + 9.1298)/1000000)
        coreThick = 9.5
        
        """ Determine the individual spar cap ply thickness distribution """
#        # The bending moment distribution of the wing
#        M_dist = [Mx(y, wingSpan, tetherTens) for y in y_range]
#        
#        # The spar cap thickness distribution
#        sparThickDist = [sparThickCalc(sigmaMax, sigmaSF, t, cLoc_range[i], M_dist[i], sparWidth, segment) for i in range(len(y_range))]
#        
#        # The number of spar cap plies along the wing
#        sparPlyNums = [ceil(max(sparThickDist[i+1], sparThickDist[i], 2.0*sparPly)/sparPly/2.0) for i in range(len(y_range)-1)]
#        
#        # The spar cap mass distribution
#        sparMassDist = [sparThickCalc(sigmaMax, sigmaSF, t, cLoc_range[i], M_dist[i], sparWidth, segment, matDens=densUD, returnMass=True) for i in range(len(y_range))]
#        
#        sparMassSummed = sum(sparMassDist)
#        
#        # Eq3.18 Mass of the spar caps (old version pre-May 2020)
##        m_caps = 2.0*(densUD*sigmaSF)/(sigmaMax*t)*(14./144.)*tetherTens*wingSpan*aspectRatio
#        
#        # Eq3.17 Mass of the spar caps (new version May 2020)
#        m_caps = 0.25*(densUD*sigmaSF)/(sigmaMax*t)*(16.0/18.0 - pi/4.0)*tetherTens*wingSpan*aspectRatio
        
        sparInputs = [sigmaMax, sigmaSF, sparWidth, sparPly, densUD]
        
        sparPlyNums, sparMassSummed, m_caps = sparDistribution(wingSpan, tetherTens, wingArea, aspectRatio, segments, chordRatio_Main, t, sparInputs)
         
        """ Determine the single shear web ply thickness distribution """
        # The shear force distribution of the wing
        Fy_dist = [Fy(y, wingSpan, tetherTens) for y in y_range]
        
        # The shear web thickness distribution
        shearThickDist = [shearThickCalc(tauMaxShear, tauShearSF, Fy_dist[i], t, cLoc_range[i], segment) for i in range(len(y_range))]
        
        # The number of shear web plies along the wing
        shearPlyNums = [ceil(max(shearThickDist[i+1], shearThickDist[i], 2.0*shearPly)/shearPly) for i in range(len(y_range)-1)]
        
        # The shear web mass distribution
        shearMassDist = [shearThickCalc(tauMaxShear, tauShearSF, Fy_dist[i], t, cLoc_range[i], segment, matDens=densShear, returnMass=True) for i in range(len(y_range))]
        
        shearMassSummed = sum(shearMassDist)
        
        # Eq3.25 Mass of the shear web
        m_web = (2./3.)*(densShear*tauShearSF)/(tauMaxShear*pi)*tetherTens*wingSpan
        
#        # Wolfram alpha => integral (rho*S/tau)*((4T/(pi*b))*(b/4)*((pi/2) - (asin(x/(b/2)) + (x/(b/2))*(1 - (x/b/2)^2)^0.5))) from 0 to b/2
#        m_webNew = (15.0*sqrt(15.0) - 52.0)*tauShearSF*densShear*wingSpan*tetherTens/(24*pi*tauMaxShear)
        
        
        """ Determine the skin ply thickness distribution """
        # The shear force distribution of the wing
        My_dist = [My(y, V, Cm, wingArea, wingSpan, tetherTens, rho) for y in y_range]
        
        # The shear web thickness distribution
        skinThickDist = [skinThickCalc(tauMaxSkin, tauSkinSF, My_dist[i], gamma, c_range[i], segment) for i in range(len(y_range))]
        
        # The number of shear web plies along the wing
        skinPlyNums = [ceil(max(skinThickDist[i+1], skinThickDist[i], 2.0*skinPly)/skinPly) for i in range(len(y_range)-1)]
        
        # The shear web mass distribution
        skinMassDist = [skinThickCalc(tauMaxSkin, tauSkinSF, My_dist[i], gamma, c_range[i], segment, matDens=densShear, returnMass=True) for i in range(len(y_range))]
        
        skinMassSummed = sum(skinMassDist)
        
        # Skin mass Eq3.39 (old version pre-May 2020)
#        m_skin = densSkin*tauSkinSF/tauMaxSkin*(2.0 * pi**2.0)/(a*(1.0 + t))*0.5*rho*average(c_range)*Cm*(V**2.0)*((wingSpan/4.0)**2.0)*((pi/2.0)**2.0 - 1.0)
        
        # Skin mass Eq3.38 (new version May 2020)
        m_skin = densSkin*tauSkinSF/tauMaxSkin*(pi)/(2.0*a*(1.0 + t))*0.5*rho*wingArea*Cm*(V**2.0)*(wingSpan/4.0)*((pi/2.0)**2.0 - 1.0)
        
        
        
        """ Check against input mass values and scale accordingly """
        c_out = [max(c_range[val],c_range[val+1]) for val in range(len(c_range)-1)]
        c_outShort = list(chordRatio_Main*array(c_out))
        
        skinsArray, sparsArray, websArray = arrayMasses(skinPlyNums, skinPly, a, c_out, c_outShort, t, segment, densSkin, sparPlyNums, sparPly, sparWidth, densUD, shearPlyNums, shearPly, densShear)
        
        actualSkinMass = sum(skinsArray)
        actualSparMass = sum(sparsArray)
        actualShearMass = sum(websArray)
        
        targetSkinMass = massInputs[0][4,i]
        targetSparMass = massInputs[0][2,i]
        targetShearMass = massInputs[0][3,i]
        
#        scalingSkin = ceil(targetSkinMass/actualSkinMass)
#        scalingSpar = ceil(targetSparMass/actualSparMass)
#        scalingShear = ceil(targetShearMass/actualShearMass)
        
#        scalingSkin = targetSkinMass/actualSkinMass
#        scalingSpar = targetSparMass/actualSparMass
#        scalingShear = targetShearMass/actualShearMass
        
        scalingSkin = m_skin/skinMassSummed
        scalingSpar = m_caps/sparMassSummed
        scalingShear = m_web/shearMassSummed
        
        
#         Rough scaling approach
#         Attempt 1 (ignore)
#        X = 240.0/42.0*28.0/12.0*12.5/12.0*0.18/0.21
#        Y = 240.0/42.0*28.0/12.0
#        mat1 = np.matrix([[1,0,0,1],
#                          [1,0,1,0],
#                          [0,1,0,-X],
#                          [0,1,-Y,0]])
#        ans = np.matrix([587, 45.2,0,0])
#
#        newAns = np.matmul(ans, np.linalg.inv(mat1))
#        
#        Attempt 2:
#        Used to find the contribution of spar caps and web to the total mass
#        Formulas for X and Y from Eq 3.19 and Eq 3.25 in 4D197
#        Values for X and Y estimated for the present analysis (for AP-4) and 
#        "Vincent_inputs_RVO" powerpoint file for AP3
#        Once values were found for spars and web, the input tether tension above
#        was changed until it resulted in spar and web mass values within a few percent
#        Ideally the material strength values would be changed to match
#        Ok for now (I guess) and results in "expected" wing mass for baseline prepregs
#        X = 272.0/42.0*32.0/12.0*12.5/12.0*0.118/0.21
#        Y = 272.0/42.0*32.0/12.0
#        mat1 = np.matrix([[1/X,1/Y],
#                          [1,1]])
#        ans = np.matrix([[45.2], [587]])
#
#        newAns = np.matmul(np.linalg.inv(mat1), ans)
#        print("m_caps_AP4: ", newAns[0,0])
#        print("m_webs_AP4: ", newAns[1,0])
#        print("ratio: ", newAns[0,0]/newAns[1,0])
        
        
        
        
#        scaleSkin = ones(40)
#        scaleSpar = ones(40)
#        scaleShear = ones(40)
#        
#        for j in range(40):
#            if(j>=14 and j<=26):
#                scaleSkin[j] = scalingSkin
#                scaleSpar[j] = scalingSpar
#            
#            if(j>=4 and j<=36):
#                scaleShear[j] = scalingShear
#        
#        skinPlyNums = array(skinPlyNums)*scaleSkin
#        sparPlyNums = array(sparPlyNums)*scaleSpar
#        shearPlyNums = array(shearPlyNums)*scaleShear
        print("Name: Summed ideal mass, Formula ideal mass, Difference, Stepwise mass")
        print("Spars: ", round(sparMassSummed,2), round(m_caps,2), round(scalingSpar,4), round(actualSparMass,2))
        print("Skins: ", round(skinMassSummed,2), round(m_skin,2), round(scalingSkin,4), round(actualSkinMass,2))
        print("Webs: ", round(shearMassSummed,2), round(m_web,2), round(scalingShear,4), round(actualShearMass,2))
        
#        skinsArray, sparsArray, websArray = arrayMasses(skinPlyNums, skinPly, a, c_out, c_outShort, t, segment, densSkin, sparPlyNums, sparPly, sparWidth, densUD, shearPlyNums, shearPly, densShear)
#        
#        actualSkinMass = sum(skinsArray)
#        actualSparMass = sum(sparsArray)
#        actualShearMass = sum(websArray)
#        
#        massOutputs[2,i] = actualSkinMass
#        massOutputs[0,i] = actualSparMass
#        massOutputs[1,i] = actualShearMass
#        
#        massOutputs[5,i] = scalingSkin
#        massOutputs[3,i] = scalingSpar
#        massOutputs[4,i] = scalingShear
        
        
        """
        Create input csv files for cost model
        """
#        outputFile = "\Area "+str(int(round(wingArea/1000000,0)))+" Tension "+str(int(round(tetherTens/1000,0)))
#        
#        try:
#            os.mkdir(directory+"\Input Range"+outputFile)
#        except FileExistsError:
#            pass
#        
#        fileName = "\\" + UDname + "_SparThickness.csv"
#        header = "spar_thickness (plies)"
#        savetxt(directory+"\Input Range"+outputFile+fileName, sparPlyNums, fmt="%.0i", header=header, delimiter=",")
#        
#        fileName = "\\" + SkinName + "_SkinThickness.csv"
#        header = "skin_thickness (plies), core_thickness_LE (mm), core_thickness_TE (mm)"
#        coreThickDist = array([coreThick for x in range(len(c_out))])
#        combined = array([skinPlyNums, coreThickDist, coreThickDist])
#        combined = transpose(combined)
#        savetxt(directory+"\Input Range"+outputFile+fileName, combined, fmt="%.0i", header=header, delimiter=",")
#        
#        fileName = "\\" + ShearName + "_WebThickness.csv"
#        header = "web_thickness (plies), core_thickness (mm)"
#        combined = array([shearPlyNums, coreThickDist])
#        combined = transpose(combined)
#        savetxt(directory+"\Input Range"+outputFile+fileName, combined, fmt="%.0i", header=header, delimiter=",")
#        
#        fileName = "\Chord.csv"
#        header = "chord (m)"
#        c_outShort = list(array(c_outShort)/1000)
#        savetxt(directory+"\Input Range"+outputFile+fileName, c_outShort, fmt="%.3f", header=header,  delimiter=",")
#        
#        fileName = "\SparLocation.csv"
#        header = "spar_width (m)"
#        sparLoc = [sparWidth/1000.0 for x in range(len(c_out))]
#        savetxt(directory+"\Input Range"+outputFile+fileName, sparLoc, fmt="%.3f", header=header,  delimiter=",")
#        
#        fileName = "\WebLocation.csv"
#        header = "web_LE_loc (x/c), web_TE_loc (x/c)"
#        webLoc1 = [0.25 for x in range(len(c_out))]
#        webLoc2 = [0.4 for x in range(len(c_out))]
#        combined = array([webLoc1, webLoc2])
#        combined = transpose(combined)
#        savetxt(directory+"\Input Range"+outputFile+fileName, combined, fmt="%.3f", header=header,  delimiter=",")
        
        
        
    massOutputs = transpose(massOutputs)


