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
import volmdlr.primitives3D as p3d
from dessia_common import DessiaObject
from typing import List,Tuple
import numpy as npy
from scipy.optimize import minimize
# =============================================================================

class Shaft(DessiaObject):

    def __init__(self, pos_x: float, pos_y: float,length: float, name: str=''):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.name = name
        self.length=length
        self.diameter=0.04

        DessiaObject.__init__(self,name=name)

    def plot(self, ax=None):
        if ax is None:
            _, ax = plt.subplots()
            ax.set_aspect('equal')
        plt.plot(self.pos_x, self.pos_y, '*')

    def volmdlr_primitives(self):
        primitives = []
        pos = vm.Point3D((self.pos_x, self.pos_y, self.length/2))
        axis = vm.Vector3D((0,0,1))
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


    def plot(self, position, ax=None):
        if ax is None:
            _, ax = plt.subplots()
            ax.set_aspect('equal')
        pos_x = position[0]
        pos_y = position[1]
        rayon = self.diameter/2.
        circle = patches.Circle((pos_x, pos_y), rayon, color='r', fill=False)
        ax.add_patch(circle)

    def volmdlr_primitives(self, xy_position, z_position):
        primitives = []
        pos = vm.Point3D((xy_position[0], xy_position[1], z_position))
        axis = vm.Vector3D((0,0,1))
        radius = self.diameter/2
        length = self.length
        cylinder = p3d.Cylinder(pos, axis, radius, length)
        primitives.append(cylinder)
        return primitives
 # =============================================================================

class Gear(DessiaObject):
    """
    Pignon
    """
    def __init__(self, diameter: float, length: float, shaft: Shaft,name: str=''):
        self.diameter = diameter
        self.length = length
        self.name = name
        self.shaft=shaft
        DessiaObject.__init__(self,name=name)



    def plot(self,ax=None):
        if ax is None:
            _, ax = plt.subplots()
            ax.set_aspect('equal')
        circle = patches.Circle((self.shaft.pos_x, self.shaft.pos_y),
                                self.diameter/2.,
                                color='b',
                                fill=False)
        ax.add_patch(circle)

    def volmdlr_primitives(self, z_position):
        primitives = []
        pos = vm.Point3D((self.shaft.pos_x,self.shaft.pos_y, z_position))
        axis = vm.Vector3D((0,0,1))
        cylinder = p3d.Cylinder(pos, axis, self.diameter/2, self.length)
        primitives.append(cylinder)
        return primitives

    def mass(self):
        return 7500 *math.pi*self.length*(self.diameter/2)**2

# =============================================================================

class Mesh(DessiaObject):
    """
    Relation d'engrènement
    """
    def __init__(self, gear1: Gear, gear2: Gear, name: str=''):
        self.gear1 = gear1
        self.gear2 = gear2
        self.gears = [gear1, gear2]
        self.name = name
        DessiaObject.__init__(self,name=name)




# =============================================================================


class Reductor(DessiaObject):
    """
    Architecture du réducteur
    """
    def __init__(self, motor: Motor, shafts:List[Shaft], meshes: List[Mesh], name: str = ''):
        self.shafts = shafts
        self.meshes = meshes
        self.name = name
        self.motor = motor
        self.offset = 0.2
        DessiaObject.__init__(self,name=name)

    def speed_output(self):

        output_speed=self.motor.speed
        for mesh in self.meshes:
            output_speed = output_speed*mesh.gear1.diameter/mesh.gear2.diameter
        return output_speed

    def update(self, x):
        """
        Mets à jour l'architecture pendant l'optimisation
        """
        i=0
        for shaft in self.shafts:
            shaft.pos_x=x[i]
            shaft.pos_y=x[i+1]
            i+=2
        for mesh in self.meshes:
            for gear in [mesh.gear1, mesh.gear2]:

                gear.diameter = x[i]
                i += 1

    def plot(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()
            ax.set_aspect('equal')
        self.motor.plot(position=[self.shafts[0].pos_x, self.shafts[0].pos_y], ax=ax)
        for shaft in self.shafts:
            shaft.plot(ax=ax)
        for meshe in self.meshes:
            meshe.gear1.plot(ax=ax)
            meshe.gear2.plot(ax=ax)
        ax.axis('scaled')

    def volmdlr_primitives(self):
        primitives = []
        primitives.extend(self.motor.volmdlr_primitives(xy_position=[self.shafts[0].pos_x, self.shafts[0].pos_y], z_position=self.motor.length/2))
        z_previous_position = self.motor.length/2+self.offset
        for shaft in self.shafts:
            primitives.extend(shaft.volmdlr_primitives())
            for mesh in self.meshes:
                if mesh.gear1.shaft==shaft:
                    z_position = z_previous_position+mesh.gear1.length/2
                    primitives.extend(mesh.gear1.volmdlr_primitives(z_position=z_position))
                    primitives.extend(mesh.gear2.volmdlr_primitives(z_position=z_position))
                    z_previous_position = z_position+mesh.gear2.length/2+self.offset

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
            for gear in [mesh.gear1, mesh.gear2]:
                bounds.append([0.1, ((y_min_max[1]-y_min_max[0])**2 + (x_min_max[1]-x_min_max[0])**2)**(1/2)])
        self.bounds = npy.array(bounds)

    def objective(self, x):
        self.reductor.update(x)
        speed = self.reductor.speed_output()
        fonctionnelle = 0

        fonctionnelle += (self.speed_output- speed)**2

        previous_radius_gear_1 = 0
        previous_radius_gear_2 = 0
        previus_radius_shaft = 0
        for mesh in self.reductor.meshes:
            shaft_gear1=mesh.gear1.shaft
            shaft_gear2=mesh.gear2.shaft
            center_distance = ((shaft_gear1.pos_x-shaft_gear2.pos_x)**2+(shaft_gear1.pos_y-shaft_gear2.pos_y)**2)**(1/2)

            if center_distance != mesh.gear1.diameter/2+mesh.gear2.diameter/2:
                fonctionnelle += ((mesh.gear1.diameter/2+mesh.gear2.diameter/2-center_distance)*1000)**2

            if shaft_gear2.pos_x < shaft_gear1.pos_x:
                fonctionnelle += ((shaft_gear1.pos_x-shaft_gear2.pos_x)*10)**2

            if shaft_gear2.pos_y < shaft_gear1.pos_y:
                fonctionnelle += ((shaft_gear1.pos_y-shaft_gear2.pos_y)*10)**2

            if previous_radius_gear_1:
                
                if mesh.gear1.diameter/2 > previous_radius_gear_1+previous_radius_gear_2-previus_radius_shaft:
                    fonctionnelle += ((mesh.gear1.diameter/2-(previous_radius_gear_1+previous_radius_gear_2-previus_radius_shaft))*10)**2
                    
                if (mesh.gear1.diameter+mesh.gear2.diameter-shaft_gear2.diameter)/2 < previous_radius_gear_2:
                    fonctionnelle += (((mesh.gear1.diameter+mesh.gear2.diameter)/2-previous_radius_gear_2)*10)**2


            for gear in [mesh.gear1,mesh.gear2]:
                if gear.shaft.pos_x-gear.diameter/2 < self.x_min_max[0]:
                    fonctionnelle += (gear.shaft.pos_x-gear.diameter/2-self.x_min_max[0])**2

                if gear.shaft.pos_x+gear.diameter/2 > self.x_min_max[1]:
                    fonctionnelle += (gear.shaft.pos_x-gear.diameter/2-self.x_min_max[1])**2

                if gear.shaft.pos_y-gear.diameter/2 < self.y_min_max[0]:
                    fonctionnelle += (gear.shaft.pos_y-gear.diameter/2-self.y_min_max[0])**2

                if gear.shaft.pos_y+gear.diameter/2 > self.y_min_max[1]:
                    fonctionnelle += (gear.shaft.pos_y-gear.diameter/2-self.y_min_max[1])**2
                    
            previous_radius_gear_1 = mesh.gear1.diameter/2
            previous_radius_gear_2 = mesh.gear2.diameter/2
            previus_radius_shaft = shaft_gear1.diameter/2



        fonctionnelle += self.reductor.mass()/10

        return fonctionnelle


    def cond_init(self):
        x0 = []
        for interval in self.bounds:
            x0.append((interval[1]-interval[0])*float(npy.random.random(1))+interval[0])
        return x0

    def minimize(self, max_loops=1000):
        valid = True
        count = 0
        while valid and count < max_loops:
            x0 = self.cond_init()
            self.reductor.update(x0)
            res = minimize(self.objective, x0, bounds=self.bounds)
            count += 1
            if  res.success:
                print(count)
                self.reductor.update(res.x)
                valid = False
                return res
            if count > max_loops:
                valid = False
                return res
        return res




