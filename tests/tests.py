# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 09:29:55 2021

@author: edward
"""

import ManuCostModel as man
import os
from ManuCostModel.MapParameters import ReadInputs, ReadInputsXML, ConsistencyCheck

materials_DB = {'fabric': {'Fabric 1': {'material': 'carbon',
                               'width': 1270.0,
                               'length': 91440.0,
                               'thickness (cured)': 0.39,
                               'areal weight': 300.0,
                               'cost': 5.49,
                               'density of fibres': 1780.0,
                               'fibre volume fraction': 0.437,
                               'fibre content': 0.55}},
                     'resin': {'Resin 1': {'material': 'epoxy',
                               'hardener name': 'System 3120',
                               'density': 1130.0,
                               'resin-hardener ratio': 5.333,
                               'cost': 36.12,
                               'cure cycle': 'System3000_cureCycle.csv'}},
                     'hardener': {'Hardener 1': {'material': 'epoxy curing agent',
                               'resin name': 'System 3000',
                               'density': 1100.0,
                               'resin-hardener ratio': 5.0,
                               'cost': 10.0}},
                     'prepreg': {'Prepreg 1': {'material': 'carbon/epoxy',
                               'fabric name': 'carbon IM',
                               'resin name': 'epoxy',
                               'width': 305.0,
                               'length': 91440.0,
                               'thickness (cured)': 0.15,
                               'areal weight': 139.0,
                               'cost': 583.32,
                               'density of fibres': 1780.0,
                               'density of resin': 1210.0,
                               'fibre volume fraction': 0.53,
                               'fibre content': 0.62}},
                     'core': {'Core 1': {'material': 'Polymethacrylimide (PMI) Foam',
                               'width': 609.6,
                               'length': 1219.2,
                               'thickness': 9.5,
                               'density': 51.0,
                               'areal weight': 486.0,
                               'cost': 5.57}},
                     'coating': {'Gel Coat 1': {'material': 'epoxy',
                               'thickness (cured)': 0.2,
                               'density': 1130.0,
                               'cost': 3.63}},
                     'adhesive': {'Adhesive 1': {'material': 'epoxy',
                               'cost': 31.35,
                               'cure cycle': 'DP490_cureCycle.csv'}},
                     'consumables': {'Mould release': {'cost': 31.35,
                               'areal weight': 1.0,
                               'scaling variable': 'Surface Area',
                               'scrap_rate': 0.0},
                              'Peel ply': {'cost': 39.0,
                               'areal weight': 181.25,
                               'scaling variable': 'Surface Area',
                               'scrap_rate': 0.2},
                              'Breather fabric': {'cost': 6.0,
                               'areal weight': 1331.25,
                               'scaling variable': 'Surface Area',
                               'scrap_rate': 0.2},
                              'Flow media': {'cost': 17.0,
                               'areal weight': 390.63,
                               'scaling variable': 'Surface Area',
                               'scrap_rate': 0.2},
                              'Paint': {'cost': 0.0,
                               'areal weight': 0.0,
                               'scaling variable': 'Surface Area',
                               'scrap_rate': 0.2}}}

production_methods_DB = {'Method 1': 
                         {'step 01': {'name': 'Fabric cutting',
                                     'labourScaling': ['Ply Length', 'fabricCutRate'],
                                     'labourHours': 0.0,
                                     'staff': 1.0,
                                     'activity': 'preform',
                                     'capitalEquipment': ['Ply cutter'],
                                     'materials': 'fabric',
                                     'materialScaling': ['Ply Surface Area', 'areal weight'],
                                     'scrapRate': 0.25,
                                     'scrapVar': 'fabric',
                                     'consumables': ['N/A']},
                         'step 02': {'name': 'Core cutting',
                                     'labourScaling': ['Core Ply Length', 'coreCutRate'],
                                     'labourHours': 0.0,
                                     'staff': 1.0,
                                     'activity': 'preform',
                                     'capitalEquipment': ['N/A'],
                                     'materials': 'core',
                                     'materialScaling': ['Core Ply Surface Area', 'areal weight'],
                                     'scrapRate': 0.25,
                                     'scrapVar': 'core',
                                     'consumables': ['N/A']},
                         'step 03': {'name': 'Mould preparation',
                                     'labourScaling': ['Surface Area', 'mouldPrep'],
                                     'labourHours': 0.0,
                                     'staff': 2.0,
                                     'activity': 'preform',
                                     'capitalEquipment': ['Lifting equipment', 'mould scenario 2'],
                                     'materials': 'N/A',
                                     'scrapRate': 'N/A',
                                     'scrapVar': 'N/A',
                                     'consumables': ['Mould release']},
                         'step 04': {'name': 'Gel coat application',
                                     'labourScaling': ['Surface Area', 'gelCoatRate'],
                                     'labourHours': 0.0,
                                     'staff': 2.0,
                                     'activity': 'preform',
                                     'capitalEquipment': ['Gel coat equipment'],
                                     'materials': 'coating',
                                     'materialScaling': ['Surface Area', 'density', 'thickness (cured)'],
                                     'scrapRate': 0.05,
                                     'scrapVar': 'coating',
                                     'consumables': ['N/A']},
                         'step 05': {'name': 'Fabric layup',
                                     'labourScaling': ['Ply Surface Area', 'fabricLayup'],
                                     'labourHours': 0.0,
                                     'staff': 2.0,
                                     'activity': 'preform',
                                     'capitalEquipment': ['N/A'],
                                     'materials': 'N/A',
                                     'scrapRate': 'N/A',
                                     'scrapVar': 'N/A',
                                     'consumables': ['N/A']},
                         'step 06': {'name': 'Core layup',
                                     'labourScaling': ['Core Ply Surface Area', 'coreLayup'],
                                     'labourHours': 0.0,
                                     'staff': 1.0,
                                     'activity': 'preform',
                                     'capitalEquipment': ['N/A'],
                                     'materials': 'N/A',
                                     'scrapRate': 'N/A',
                                     'scrapVar': 'N/A',
                                     'consumables': ['N/A']},
                         'step 07': {'name': 'Spar installation',
                                     'labourScaling': 'N/A',
                                     'labourHours': 1.0,
                                     'staff': 2.0,
                                     'activity': 'preform',
                                     'capitalEquipment': ['N/A'],
                                     'materials': 'N/A',
                                     'scrapRate': 'N/A',
                                     'scrapVar': 'N/A',
                                     'consumables': ['N/A']},
                         'step 08': {'name': 'Consumables layup',
                                     'labourScaling': ['Surface Area', 'consLayup'],
                                     'labourHours': 0.0,
                                     'staff': 2.0,
                                     'activity': 'cure',
                                     'capitalEquipment': ['N/A'],
                                     'materials': 'N/A',
                                     'scrapRate': 'N/A',
                                     'scrapVar': 'N/A',
                                     'consumables': ['Vacuum film',
                                                     'Peel ply',
                                                     'Flow media',
                                                     'Release film',
                                                     'Sealant tape',
                                                     'VAP membrane',
                                                     'Resin tube']},
                         'step 09': {'name': 'Vacuum application',
                                     'labourScaling': 'N/A',
                                     'labourHours': 0.5,
                                     'staff': 1.0,
                                     'activity': 'cure',
                                     'capitalEquipment': ['Vacuum unit'],
                                     'materials': 'N/A',
                                     'scrapRate': 'N/A',
                                     'scrapVar': 'N/A',
                                     'consumables': ['N/A']},
                         'step 10': {'name': 'Infusion',
                                     'labourScaling': 'N/A',
                                     'labourHours': 2.0,
                                     'staff': 1.0,
                                     'activity': 'cure',
                                     'capitalEquipment': ['N/A'],
                                     'materials': 'resin',
                                     'materialScaling': ['Ply Surface Area', 'areal weight'],
                                     'scrapRate': 0.076,
                                     'scrapVar': 'resin',
                                     'consumables': ['N/A']},
                         'step 11': {'name': 'Cure',
                                     'labourScaling': 'N/A',
                                     'labourHours': 'material definition',
                                     'staff': 1.0,
                                     'activity': 'cure',
                                     'capitalEquipment': ['Oven'],
                                     'materials': 'N/A',
                                     'scrapRate': 'N/A',
                                     'scrapVar': 'N/A',
                                     'consumables': ['N/A']},
                         'step 12': {'name': 'Remove consumables',
                                     'labourScaling': 'N/A',
                                     'labourHours': 1.0,
                                     'staff': 1.0,
                                     'activity': 'cure',
                                     'capitalEquipment': ['N/A'],
                                     'materials': 'N/A',
                                     'scrapRate': 'N/A',
                                     'scrapVar': 'N/A',
                                     'consumables': ['N/A']},
                         'step 13': {'name': 'Demould',
                                     'labourScaling': 'N/A',
                                     'labourHours': 1.0,
                                     'staff': 2.0,
                                     'activity': 'cure',
                                     'capitalEquipment': ['N/A'],
                                     'materials': 'N/A',
                                     'scrapRate': 'N/A',
                                     'scrapVar': 'N/A',
                                     'consumables': ['N/A']},
                         'step 14': {'name': 'Surface inspection',
                                     'labourScaling': 'N/A',
                                     'labourHours': 5.0,
                                     'staff': 1.0,
                                     'activity': 'assembly',
                                     'capitalEquipment': ['NDT equipment'],
                                     'materials': 'N/A',
                                     'scrapRate': 'N/A',
                                     'scrapVar': 'N/A',
                                     'consumables': ['N/A']}}}

manufacturing_DB = {'spar': {'fabric': 'Fabric 1',
                     'resin': 'Resin 1',
                     'hardener': 'Hardener 1',
                     'prepreg': 'N/A',
                     'core': 'N/A',
                     'adhesive': 'N/A',
                     'coating': 'N/A',
                     '# items': 1,
                     'preforming': 'Method 1',
                     'preforming_steps_ignore': ['step 02', 'step 04', 'step 06', 'step 08'],
                     'curing': 'N/A',
                     'assembly': 'N/A'}}

inputVars = {'main wing element': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'aileron port': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'aileron starboard': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'flap port': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'flap starboard': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'flaperon port': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'flaperon starboard': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'fuselage port': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'fuselage starboard': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'horizontal tail': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'vertical tail port': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}, 'vertical tail starboard': {'spar1': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'spar2': {'Surface Area': 14.99, 'Ply Surface Area': 566.02, 'Ply Length': 2515.66, 'Part Length': 27.0}, 'web1': {'Surface Area': 7.24, 'Ply Surface Area': 260.88, 'Ply Length': 441.78, 'Bondline': 55.6, 'Part Length': 27.0, 'Core Surface Area': 76.66, 'Core Ply Length': 192.76, 'Core Ply Surface Area': 72.66}, 'skin1': {'Surface Area': 44.57, 'Ply Surface Area': 274.88, 'Ply Length': 281.82, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 155.76, 'Core Ply Length': 351.39, 'Core Ply Surface Area': 155.76}, 'skin2': {'Surface Area': 40.87, 'Ply Surface Area': 252.09, 'Ply Length': 264.26, 'Bondline': 92.96, 'Part Length': 44.82, 'Core Surface Area': 139.03, 'Core Ply Length': 322.11, 'Core Ply Surface Area': 139.03}, 'wing1': {'Surface Area': 129.47, 'Webs Bondline': 56.0, 'Shells Bondline': 112.0, 'Shell Bondline': 56.0, 'Web Nums': 1.0}}}

directory = os.path.dirname(os.path.realpath(__file__))

structural_inputs = 'ScalingVariables.xml'

inputFileName = "manufacturingDatabase" # Replace with some example file

factory = man.CostModel.Manufacture(directory, inputFileName, scaleFile=structural_inputs)

factory.Scale(True)

materialDict = factory.MaterialDictionary(manufacturing_DB, 'spar')

component = man.CostModel.component('spar', 'spar', 'wing', matDetails=materialDict)

scalingInputs = ReadInputsXML(directory + "\\Input Databases\\" + structural_inputs)

component.scaleVars = scalingInputs[component.product][component.name+'1']

component.ProductionDefinition(manufacturing_DB, production_methods_DB)

factory.MaterialsAnalysis(component, materials_DB)

def mat_cost_test(component, materials_DB, stepNum):
    return factory.MaterialsCost(component, materials_DB, stepNum)

def mat_test_1(component, materials_DB, stepNum):
    assert mat_cost_test(component, materials_DB, stepNum) == (150.0, 823.5)
    
def mat_test_2(component, materials_DB, stepNum):
    assert mat_cost_test(component, materials_DB, stepNum) == (150.0, 823.5)
    