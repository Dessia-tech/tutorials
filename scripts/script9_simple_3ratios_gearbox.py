# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 11:29:57 2021

@author: wirajan
"""
import tutorials.Tutoriel_BV_3rapports as objects



speed = [[800, 1800], [800,1800], [1800,3200], [800, 3200], [800, 3200], [800, 3200], [800, 1100],[1100, 3200], [1100, 3200], [1600, 3200], [1600, 2400], [2400, 3200],[2000,3200]]
torque= [[0,12],[12,18],[0,18],[18,25], [25,35], [35,50], [55, 80],[50,70],[70,95],[85,105], [105,125], [105,125],[125,160]]
efficiency = [0.14, 0.18, 0.18, 0.22, 0.26, 0.29, 0.32,0.32, 0.34, 0.35,0.35, 0.36, 0.32]
data = objects.Data(speed = speed, torque = torque, efficiency = efficiency)
motor = objects.Motor(speed=1000, torque = 80, data = data)
gearbox = objects.GearBox(motor = motor)
speeds = [784, 1100, 1792]
torques = [475, 340, 200]

optimizer = objects.GearBoxOptimizer(gearbox = gearbox, ratios_min_max=[0.5,4.2], speeds = speeds, torques = torques, number_ratios=3)

results = optimizer.optimize(10000)
print("ALL RESULTS AVAILABLE:")
for result in results[0]:
    print('ratios:',result.ratios)
    print('efficiencies: ', result.efficiencies)
    print('\n')

print('VALUES FOR THE OBJECTIVE FUNCTION:')
print(results[1])
print('\n')

print('BEST RESULTS:')
functional_min=min(results[1])
for i, (gearbox, functional) in enumerate(zip(results[0],results[1])):
    if functional == functional_min:
        print('Ratios:', gearbox.ratios)
        print('Efficiencies:', gearbox.efficiencies)
        print('\n')



