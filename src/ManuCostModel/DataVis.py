# -*- coding: utf-8 -*-
"""
Modules for Data Visualisation

Edward Fagan
"""

from numpy import array, arange
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import webcolors

""" Data visualisation """
# Convert rgd values to hexadecimal values for the colour code
def rgb2hex(rgb):
    newVal = '#%02x%02x%02x' % rgb
    return newVal

# Make patch spines invisible on plot
def invisiblePatchSpines(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    
    for val in ax.spines.values():
        val.set_visible(False)

# Create a list of colour codes in shades of red, green or blue
def randomColour(colourInp, num_bars, shadedBars):
    
    if(shadedBars is True):
        base = colourInp
        
        rgbl = webcolors.name_to_rgb(base)
            
        chng = 0
        if base in ['red', 'green', 'blue']:
            for i, val in enumerate(rgbl):
                if val > 0:
                    chng = i
        
        segment = int(max(rgbl)/num_bars)
        colour_list = [webcolors.rgb_to_hex(rgbl)]
        
        rgbl = list(rgbl)
        
        for vals in range(num_bars-1):
            rgbl[chng] = rgbl[chng] - segment
            
            webcolors.IntegerRGB(rgbl[0], rgbl[1], rgbl[2])
            colour_list.append(webcolors.rgb_to_hex(rgbl))
            
    else:
        colour_list = []
        
        for base in colourInp:
                
            rgbl = webcolors.name_to_rgb(base)
            
            colour_list.append(webcolors.rgb_to_hex(rgbl))
    
    return colour_list

# Create a bar plot
def barPlot(plotData, percentDisplay=False, barLabelDisplay=False, secondAxis=False, secondAxisVars=None):
    
    plotInfo, data, dataLabels, colourSet, legendDisplay = plotData
    
    sources = tuple([val[0] for val in plotInfo])
    ylabel = ('Cost (€)')
    
    x_pos = arange(len(sources)) + (array([len(dat) for dat in data]) - 1.0)*0.25/2.0
    
    fig = figure(figsize=(10,8))
    ax = fig.add_subplot(111)
    
    patch_handles = []
    legend_handles = []
    
    for label in range(len(data)):
        
        data_set = data[label]
        patch_handles.append([])
        h_pos = label
        
        for x, indiv_data in enumerate(data_set):
            
            # Check if each bar colour has been specified or if the shaded option is desired
            if(len(colourSet[label][x]) == len(data[label][x])):
                shadedBars = False
                colourInp = colourSet[label][x]
            else:
                shadedBars = True
                colourInp = colourSet[label][x][0]
            
            colour_list = randomColour(colourInp, len(data[label][x]), shadedBars)
            
            
            patch_handles[label].append([])
            bottom = (0.0) # Bottom alignment of data
            
            for i, d in enumerate(indiv_data):
                # Horizontal bar chart option
                bar = ax.bar(h_pos, d, 0.2, bottom=bottom, color=colour_list[i])
                patch_handles[label][x].append(bar)
                
                # Accumulate the blocks in the bar
                bottom += (d)
                
                try:
                    if(legendDisplay[label][x][i] == 1):
                        legend_handles.append(bar)
                except IndexError:
                    pass
                
            h_pos += 0.25
    
    legendList = []
    
    # Loop through the bar segments and label each one
    for i1, patch_holder in enumerate(patch_handles):
        
        for k, patch_batch in enumerate(patch_holder):
            
            for j, handle in enumerate(patch_batch):
                
                
                for i, patch in enumerate(handle.get_children()):
                    
                    if(percentDisplay is True):
                        percentages = array(data[i1][k])/sum(data[i1][k])*100
                    else:
                        percentages = data[i1][k]
                    
                    bl = patch.get_xy()
                    x = patch.get_width() + bl[0]
                    y = 0.5*patch.get_height() + bl[1]
                    
                    if(percentDisplay is True):
                        legendText = dataLabels[i1][k][j]
                        barSegText = " (%d.0%%)" % (percentages[j])
                        if(barLabelDisplay is True):
                            ax.text(x, y, legendText+barSegText, ha='left')
                    else:
                        legendText = dataLabels[i1][k][j]
                        barSegText = " (€%d)" % (percentages[j])
                        if(barLabelDisplay is True):
                            ax.text(x, y, legendText+barSegText, ha='left')
                    
                    try:
                        if(legendDisplay[i1][k][j] == 1):
                            legendList.append(legendText)
                    except IndexError:
                        pass
    
    
    ax.set_ylabel(ylabel, fontsize=12)
    
    if(len(legend_handles) > 0):
        ax.legend(legend_handles, legendList)
    
    
    if(secondAxis is True):
        
        fig.subplots_adjust(bottom=0.2)
        ax2 = ax.twiny()
        
        ax2.spines["bottom"].set_position(("axes", -0.15))
        #invisiblePatchSpines(ax2)
        ax2.spines["bottom"].set_visible(True)
        
        ax2.xaxis.set_label_position('bottom')
        ax2.spines['bottom'].set_position(('outward', 36))
        ax2.xaxis.set_ticks_position('bottom')
        
        ax2.set_xlim(ax.get_xlim())
        
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(sources, fontsize=12)
        
        # Hide the outer axis so only labels show
        ax2.spines['bottom'].set_visible(False)
        ax2.tick_params(bottom=False, labelbottom=True)
        
        # Set the new labels on the inner x-axis
        x_pos_new = []
        x_pos_newLabels = []
        
        for val in range(len(data)):
            for val2 in range(len(data[val])):
                x_pos_new.append(val + val2*0.25)
                x_pos_newLabels.append(secondAxisVars[val2])
        
        ax.set_xticks(x_pos_new)
        ax.set_xticklabels(x_pos_newLabels)
        
        
#        ax2.set_xlabel(r"Modified x-axis: $1/(1+X)$")
        
    else:
        ax.set_xticks(x_pos)
        ax.set_xticklabels(sources, fontsize=12)
        
    
    plt.show()



def pieChart(plotData):
    
    plotInfo, data, dataLabels, colourSet, legendDisplay = plotData
    
    # Make the figure
    fig = plt.figure(figsize=(9, 5))
    
    # Assign axis objects and make subplots as necesary
    axisObjs = []
    numPlots = 101 + len(data)*10
    
    for i in range(len(data)):
        ax1 = fig.add_subplot(numPlots)
        axisObjs.append(ax1)
        numPlots += 1
    
    fig.subplots_adjust(wspace=0.25)
    
    # Create the pie charts
    for j, ax in enumerate(axisObjs):
        
        dataFract = array(data[j][0])/sum(data[j][0])
        ax.pie(dataFract, autopct='%1.1f%%', startangle=0.0, labels=dataLabels[j][0])
        ax.set_xlabel(plotInfo[j][0], fontsize=12, weight='bold')



if(__name__ == '__main__'):
    
    # Example pie chart for visualising the full breakdown of materials, labour 
    # and equipment costs for several production methods
    plotInfo = [['VI'],
                ['LRTM'],
                ['VBO']]
    
    data = [[[5000.0, 3155.0, 1000.0]],
            [[2500.0, 2800.0, 590.0]],
            [[3250.0, 3300.0, 800.0]]]
    
    dataLabels = [[["Materials", "Equipment", "Labour"]],
                  [["Materials", "Equipment", "Labour"]],
                  [["Materials", "Equipment", "Labour"]]]
    
    plotData = plotInfo, data, dataLabels, None, None
    
    pieChart(plotData)
    
    
    # Example bar plot for visualising the full breakdown of materials, labour  
    # and equipment costs for one production method
    plotInfo = [['Material Cost (€)'],
                ['Equipment Cost (€)'],
                ['Labour Cost (€)']]
    
    data = [[[5000.0, 3155.0, 29.0, 5481.0, 3085.0]],
            [[2500.0, 315.0, 290.0, 548.0, 300.0]],
            [[2500.0, 315.0, 290.0]]]
    
    dataLabels = [[["Fabric", "Foam", "Gelcoat", "Resin", "Prepreg (incl. Resin)"]],
                  [["Lifting", "Vacuum", "Mould", "Frame", "Plumbing"]],
                  [["Fabrication", "Finishing", "In-mould"]]]
    
    colourSet = [[['red']],
                 [['green']],
                 [['blue']]]
    
    legendDisplay = [[[1,1,1,1,1]],
                     [[1,1,1,1,1]],
                     [[1,1,1]]]
    
    plotData = plotInfo, data, dataLabels, colourSet, legendDisplay
    
    barPlot(plotData, percentDisplay=True, barLabelDisplay=True)
    
    
    # Example bar plot for comparing major cost centres for multiple production 
    # methods
    plotInfo = [['Material Cost (€)'],
                ['Equipment Cost (€)'],
                ['Labour Cost (€)']]
    
    data = [[[5000.0],[1000.0]],
            [[2500.0],[4000.0]],
            [[2500.0],[1500.0]]]
    
    data = [[[5000.0]],
            [[2500.0]],
            [[2500.0]]]
    
    dataLabels = [[["LRTM"],["VI"]],
                  [["LRTM"],["VI"]],
                  [["LRTM"],["VI"]]]
    
    colourSet = [[['red'],['blue']],
                 [['red'],['blue']],
                 [['red'],['blue']]]
    
    legendDisplay = [[[1],[1]],
                     [[],[]],
                     [[],[]]]
    
    plotData = plotInfo, data, dataLabels, colourSet, legendDisplay
    
    barPlot(plotData, percentDisplay=False, barLabelDisplay=True)
    
    
    # Example bar plot for comparing the contribution of major cost centres to  
    # the total cost for multiple production methods
    plotInfo = [['VI'],
                ['LRTM'],
                ['VBO']]
    
    data = [[[5000.0, 3155.0, 1000.0]],
            [[2500.0, 2800.0, 590.0]],
            [[3250.0, 3300.0, 800.0]]]
    
    dataLabels = [[["Materials", "Equipment", "Labour"]],
                  [["Materials", "Equipment", "Labour"]],
                  [["Materials", "Equipment", "Labour"]]]
    
    colourSet = [[['red']],
                 [['green']],
                 [['blue']]]
    
    legendDisplay = [[[]],
                     [[]],
                     [[]]]
    
    plotData = plotInfo, data, dataLabels, colourSet, legendDisplay
    
    barPlot(plotData, percentDisplay=False, barLabelDisplay=True)
    
    
    # Example bar plot for comparing the contribution of major cost centres to  
    # the total cost for multiple production methods and for another variable, 
    # e.g. parts per annum
    plotInfo = [['VI'],
                ['LRTM'],
                ['VBO']]
    
    data = [[[5000.0, 3000.0, 1000.0],[4000.0, 2000.0, 500.0]],
            [[5000.0, 3000.0, 1000.0],[4000.0, 2000.0, 500.0]],
            [[5000.0, 3000.0, 1000.0],[4000.0, 2000.0, 500.0]]]
    
    dataLabels = [[["Materials (200 PPA)", "Labour (200 PPA)", "Equipment (200 PPA)"],
                   ["Materials (500 PPA)", "Labour (500 PPA)", "Equipment (500 PPA)"]],
                  [["Materials", "Labour", "Equipment"],
                   ["Materials", "Labour", "Equipment"]],
                  [["Materials", "Labour", "Equipment"],
                   ["Materials", "Labour", "Equipment"]]]
    
    colourSet = [[['blue'],['red']],
                 [['blue'],['red']],
                 [['blue'],['red']]]
    
    legendDisplay = [[[1,1,1],[1,1,1]],
                     [[],[]],
                     [[],[]]]
    
    secondVars = ['200 PPA', '500 PPA']
    
    plotData = plotInfo, data, dataLabels, colourSet, legendDisplay
    
    barPlot(plotData, percentDisplay=True, barLabelDisplay=False, 
            secondAxis=True, secondAxisVars=secondVars)
