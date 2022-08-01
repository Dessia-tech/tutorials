#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 11:05:57 2020

@author: launay
"""

import tutorials.tutorial2_powertransmission as objects

motor = objects.Motor(diameter=0.1, length=0.2, speed=120)
shafts = [objects.Shaft(pos_x=0, pos_y=0, length=0.1), objects.Shaft(pos_x=0, pos_y=0, length=0.1),
          objects.Shaft(pos_x=0, pos_y=0, length=0.1)]
meshes = []
for j, shaft in enumerate(shafts):
    if j == 1:
        gear1 = objects.Gear(diameter=0.1, length=0.01, shaft=shaft)
        gear2 = objects.Gear(diameter=0.1, length=0.01, shaft=shaft)
        meshes.append(objects.Mesh(gear, gear1))
    else:
        gear = objects.Gear(diameter=0.1, length=0.01, shaft=shaft)
meshes.append(objects.Mesh(gear2, gear))
reductor = objects.Reductor(motor, shafts, meshes)

optimizer = objects.Optimizer(reductor=reductor, speed_output=500, x_min_max=[-1, 1], y_min_max=[-1, 1])
list_reductor = optimizer.optimize()
list_reductor[0].babylonjs()