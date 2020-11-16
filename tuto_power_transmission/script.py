#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 21:37:49 2019

@author: jezequel
"""
import objects.core as objects

length_gear=0.1
offset=0.2
motor=objects.Motor(diameter=0.1,length=0.2,speed=120)
length_shaft=motor.length+offset*3+length_gear*3
shafts=[objects.Shaft(0,0,length_shaft),objects.Shaft(0,0,length_shaft),objects.Shaft(0,0,length_shaft)]
meshes=[]
for j,shaft in enumerate(shafts) :
    if j==1:
        gear1=objects.Gear(0.1,0.1,shaft)
        gear2=objects.Gear(0.1,0.1,shaft)
        meshes.append(objects.Mesh(gear,gear1))
    else:
        gear=objects.Gear(0.1,0.1,shaft)
meshes.append(objects.Mesh(gear2,gear))
reductor=objects.Reductor(motor,shafts,meshes)


optimizer=objects.Optimizer(reductor=reductor,speed_output=500,x_min_max=[-1,1],y_min_max=[-1,1])
optimizer.minimize()


