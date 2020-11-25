#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 21:32:30 2019

@author: jezequel
"""
import matplotlib.pyplot as plt
from matplotlib import patches
import math
import volmdlr as vm
import volmdlr.primitives3d as p3d
from dessia_common import DessiaObject
from typing import List,Tuple
import numpy as npy
from scipy.optimize import minimize
import copy
# =============================================================================

class Shaft(DessiaObject):

    def __init__(self, pos_x: float, pos_y: float,length: float, name: str=''):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.name = name
        self.length=length
        self.diameter=0.04
        self.z_position=self.length/2
        DessiaObject.__init__(self,name=name)

    def plot(self, ax=None):
        if ax is None:
            _, ax = plt.subplots()
            ax.set_aspect('equal')
        plt.plot(self.pos_x, self.pos_y, '*')

    def volmdlr_primitives(self):
        primitives = []
        pos = vm.Point3D(self.pos_x, self.pos_y, self.z_position)
        axis = vm.Vector3D(0,0,1)
        cylinder = p3d.Cylinder(pos, axis, self.diameter/2, self.length)
        primitives.append(cylinder)
        return primitives

    def mass(self):
        return 7500 *math.pi*self.length*(self.diameter/2)**2

# =============================================================================

class Motor(DessiaObject):

    def __init__(self, diameter: float, length: float, speed: float, name: str = ''):
        self.diameter = diameter
        self.length = length
        self.speed = speed
        self.name = name
        DessiaObject.__init__(self,name=name)
        self.z_position=self.length/2
        self.pos_x=0
        self.pos_y=0

    def plot(self, position, ax=None):
        if ax is None:
            _, ax = plt.subplots()
            ax.set_aspect('equal')
        pos_x = position[0]
        pos_y = position[1]
        rayon = self.diameter/2.
        circle = patches.Circle((pos_x, pos_y), rayon, color='r', fill=False)
        ax.add_patch(circle)

    def volmdlr_primitives(self):
        primitives = []
        pos = vm.Point3D(self.pos_x, self.pos_y, self.z_position)
        axis = vm.Vector3D(0,0,1)
        cylinder = p3d.Cylinder(pos, axis, self.diameter/2, self.length)
        primitives.append(cylinder)
        return primitives
 # =============================================================================

class Gear(DessiaObject):
    
    def __init__(self, diameter: float, length: float, shaft: Shaft,name: str=''):
        self.diameter = diameter
        self.length = length
        self.name = name
        self.shaft=shaft
        DessiaObject.__init__(self,name=name)
        self.z_position=0


    def plot(self,ax=None):
        if ax is None:
            _, ax = plt.subplots()
            ax.set_aspect('equal')
        circle = patches.Circle((self.shaft.pos_x, self.shaft.pos_y),
                                self.diameter/2.,
                                color='b',
                                fill=False)
        ax.add_patch(circle)

    def volmdlr_primitives(self):
        primitives = []
        pos = vm.Point3D(self.shaft.pos_x,self.shaft.pos_y, self.z_position)
        axis = vm.Vector3D(0,0,1)
        cylinder = p3d.Cylinder(pos, axis, self.diameter/2, self.length)
        primitives.append(cylinder)
        return primitives

    def mass(self):
        return 7500 *math.pi*self.length*(self.diameter/2)**2

# =============================================================================

class Mesh(DessiaObject):

    def __init__(self, gear1: Gear, gear2: Gear, name: str=''):
        self.gear1 = gear1
        self.gear2 = gear2
        self.gears = [gear1, gear2]
        self.name = name
        DessiaObject.__init__(self,name=name)




# =============================================================================


class Reductor(DessiaObject):
    _standalone_in_db=True
    def __init__(self, motor: Motor, shafts:List[Shaft], meshes: List[Mesh], number_solution: int = 0,name: str = ''):
        self.shafts = shafts
        self.meshes = meshes
        self.name = name
        self.motor = motor
        self.offset = 0.02
        self.number_solution=number_solution
        DessiaObject.__init__(self,name=name)
        self.mass_reductor=self.mass()
        

    def speed_output(self):

        output_speed=self.motor.speed
        for mesh in self.meshes:
            output_speed = output_speed*mesh.gear1.diameter/mesh.gear2.diameter
        return output_speed

    def update(self, x):
        i=0
        for shaft in self.shafts:
            shaft.pos_x=x[i]
            shaft.pos_y=x[i+1]
            i+=2
        for mesh in self.meshes:
            shaft_gear1=mesh.gear1.shaft
            shaft_gear2=mesh.gear2.shaft
            center_distance = ((shaft_gear1.pos_x-shaft_gear2.pos_x)**2+(shaft_gear1.pos_y-shaft_gear2.pos_y)**2)**(1/2)
            
            mesh.gear1.diameter = x[i]
            mesh.gear2.diameter = (center_distance-x[i]/2)*2
            i += 1
        self.mass_reductor=self.mass()    
        

    def plot(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()
            ax.set_aspect('equal')
        self.motor.pos_x=self.shafts[0].pos_x
        self.motor.pos_y=self.shafts[0].pos_y
        self.motor.plot(ax=ax)
        for shaft in self.shafts:
            shaft.plot(ax=ax)
        for meshe in self.meshes:
            meshe.gear1.plot(ax=ax)
            meshe.gear2.plot(ax=ax)
        ax.axis('scaled')

    def volmdlr_primitives(self):
        primitives = []
        self.motor.pos_x=self.shafts[0].pos_x
        self.motor.pos_y=self.shafts[0].pos_y
        
        primitives.extend(self.motor.volmdlr_primitives())
        z_previous_position_gear = self.motor.length+self.offset
        z_previous_position_shaft=0
        for shaft in self.shafts:
                
           
            for mesh in self.meshes:
                if mesh.gear1.shaft==shaft:
                   
                    z_position = z_previous_position_gear+mesh.gear1.length/2
                    mesh.gear1.z_position=z_position
                    mesh.gear2.z_position=z_position
                    primitives.extend(mesh.gear1.volmdlr_primitives())
                    primitives.extend(mesh.gear2.volmdlr_primitives())
                    break
                
            shaft.length= z_position+mesh.gear1.length/2+self.offset-z_previous_position_shaft
            shaft.z_position=shaft.length/2+z_previous_position_shaft
            
            primitives.extend(shaft.volmdlr_primitives())
                
            z_previous_position_gear = z_position+mesh.gear2.length/2+self.offset
            z_previous_position_shaft= z_position-mesh.gear2.length/2-self.offset
            

        return primitives

    def mass(self):
        mass = 0
        for shaft in self.shafts:
            mass += shaft.mass()
        for meshe in self.meshes:
            for gear in [meshe.gear1, meshe.gear2]:
                mass += gear.mass()
        return mass

class Optimizer(DessiaObject):
    def __init__(self, reductor: Reductor, speed_output: float, x_min_max: Tuple[float, float], y_min_max: Tuple[float, float], name: str =''):
        self.reductor = reductor
        self.x_min_max = x_min_max
        self.y_min_max= y_min_max
        self.speed_output = speed_output
        DessiaObject.__init__(self,name=name)

        bounds = []
        for shaft in reductor.shafts:
            bounds.append([x_min_max[0], x_min_max[1]])
            bounds.append([y_min_max[0], y_min_max[1]])
        for mesh in reductor.meshes:
            bounds.append([mesh.gear1.shaft.diameter, ((y_min_max[1]-y_min_max[0])**2 + (x_min_max[1]-x_min_max[0])**2)**(1/2)])
        self.bounds = bounds

    def objective(self, x):
        self.reductor.update(x)
        speed = self.reductor.speed_output()
        functional = 0

        functional += (self.speed_output- speed)**2

        previous_radius_gear_1 = 0
        previous_radius_gear_2 = 0
        previus_radius_shaft = 0
        for mesh in self.reductor.meshes:
            shaft_gear1=mesh.gear1.shaft
            shaft_gear2=mesh.gear2.shaft
            
            

            if mesh.gear2.diameter<mesh.gear2.shaft.diameter:
                  functional += 10

            if shaft_gear2.pos_x < shaft_gear1.pos_x:
                functional += 10

            if shaft_gear2.pos_y < shaft_gear1.pos_y:
                functional += 10

            if previous_radius_gear_1:
                
                if mesh.gear1.diameter/2 > previous_radius_gear_1+previous_radius_gear_2-previus_radius_shaft:
                    functional += 10
                    
                if (mesh.gear1.diameter+mesh.gear2.diameter-shaft_gear2.diameter)/2 < previous_radius_gear_2:
                    functional += 10


            for gear in [mesh.gear1,mesh.gear2]:
                
                if gear.shaft.pos_x-gear.diameter/2 < self.x_min_max[0]:
                    functional += (gear.shaft.pos_x-gear.diameter/2-self.x_min_max[0])**2
              
                if gear.shaft.pos_x+gear.diameter/2 > self.x_min_max[1]:
                    functional+= (gear.shaft.pos_x-gear.diameter/2-self.x_min_max[1])**2
                
                if gear.shaft.pos_y-gear.diameter/2 < self.y_min_max[0]:
                    functional += (gear.shaft.pos_y-gear.diameter/2-self.y_min_max[0])**2
                
                if gear.shaft.pos_y+gear.diameter/2 > self.y_min_max[1]:
                    
                    functional += (gear.shaft.pos_y-gear.diameter/2-self.y_min_max[1])**2
                    
            previous_radius_gear_1 = mesh.gear1.diameter/2
            previous_radius_gear_2 = mesh.gear2.diameter/2
            previus_radius_shaft = shaft_gear1.diameter/2



        functional += self.reductor.mass()/10

        return functional


    def cond_init(self):
        x0 = []
        for interval in self.bounds:
            x0.append((interval[1]-interval[0])*float(npy.random.random(1))+interval[0])
        return x0

    def optimize(self, max_loops: int =1000):
        valid = True
        count = 0
        list_reductor=[]
        while valid and count < max_loops:
            x0 = self.cond_init()
            self.reductor.update(x0)
            res = minimize(self.objective, x0, bounds=self.bounds)
            count += 1
            if  res.fun<10 and res.success:
                print(count)
                self.reductor.update(res.x)
                self.reductor.number_solution=len(list_reductor)
                list_reductor.append(copy.deepcopy(self.reductor))

        return list_reductor
    
class InstanciateReductor(DessiaObject):
    
    def __init__(self,motor: Motor, length_gears: float = 0.01, name: str = ''):
        self.motor=motor

        self.length_gears=length_gears
        DessiaObject.__init__(self,name=name)
        
        
    def instanciate(self):
        shafts = [Shaft(pos_x=0, pos_y=0, length=0.1), Shaft(pos_x=0, pos_y=0, length=0.1),
                  Shaft(pos_x=0, pos_y=0, length=0.1)]
        meshes = []
        for j, shaft in enumerate(shafts) :
            if j == 1:
                gear1 = Gear(diameter=0.1, length=self.length_gears, shaft=shaft)
                gear2 = Gear(diameter=0.1, length=self.length_gears, shaft=shaft)
                meshes.append(Mesh(gear, gear1))
            else:
                gear = Gear(diameter=0.1, length=self.length_gears, shaft=shaft)
        meshes.append(Mesh(gear2, gear))
        reductor = Reductor(self.motor, shafts, meshes)
        return reductor
        
    
        
        




