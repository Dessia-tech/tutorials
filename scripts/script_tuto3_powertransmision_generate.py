#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 11:05:57 2020

@author: launay
"""

import tutorials.tutorial3_powertransmission_generator as objects

motor = objects.Motor(diameter=0.1, length=0.2, speed=100)
generator = objects.Generator(motor=motor, speed_output=500, z_min_max=(4, 30))
list_reductor = generator.generate()
list_reductor_optimize = []
for reductor in list_reductor:
    # print(1)
    optimizer = objects.Optimizer(reductor=reductor, x_min_max=(-1, 1), y_min_max=(-1, 1))
    
    reductor_optimize = optimizer.optimize()
    list_reductor_optimize.append(reductor_optimize)
    # optionnel
    if len(list_reductor_optimize) == 15:
        break

