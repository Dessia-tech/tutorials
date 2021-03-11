# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 13:30:58 2021

@author: wirajan
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
import dectree as dt
import numpy as np

class Data():
    def __init__(self, speed: List[Tuple[float, float]], torque: List[Tuple[float, float]], efficiency:List[float]):
        # self.speed = [[i[0]*np.pi/30,i[1]*np.pi/30] for i in speed] 
        self.speed = speed
        self.torque = torque
        self.efficiency = efficiency 
    
    
class Motor(DessiaObject):
    def __init__(self, speed:float, torque:float, data : Data, name:str=''):
        # motor parameters
        self.speed = speed
        self.torque = torque
        self.data = data
        DessiaObject.__init__(self,name=name)
        self.z_position=0
        self.pos_x=0
        self.pos_y=0
        
    def efficiency(self, speed:float, torque:float):
        efficiency=0
        for i, spd in enumerate(self.data.speed):
            if speed > spd[0] and speed < spd[1]:
                if torque > self.data.torque[i][0] and torque < self.data.torque[i][1]:
                    efficiency = self.data.efficiency[i]
        return efficiency
        
        
class GearBox(DessiaObject):
    def __init__(self, motor: Motor, ratios=None, efficiencies=None, name:str=''):
        self.motor = motor
        self.ratios = ratios
        self.efficiencies = efficiencies
        DessiaObject.__init__(self,name=name)
        
        

        

class GearBoxOptimizer(DessiaObject):
    def __init__(self, gearbox: GearBox, ratios_min_max:Tuple[float, float], speeds=None, torques=None, number_ratios:int=3):
        self.gearbox = gearbox
        self.speeds = speeds
        self.torques = torques
        self.ratios_min_max = ratios_min_max
        self.number_ratios = number_ratios
        
        
        bounds=[]
        for ratio in range(self.number_ratios):
            bounds.append([ratios_min_max[0],ratios_min_max[1]])
        self.bounds = bounds
        
    def objective(self, x):
        " it's important to note that here  we use ratio as being defined by w_in/w_out"
        efficiencies=[]
        objective_function = 0
        for i,(speed, torque) in enumerate(zip(self.speeds, self.torques)):
            ratio = x[i]
            motor_speed = speed*ratio
            motor_torque = torque/ratio
            efficiency = self.gearbox.motor.efficiency(motor_speed, motor_torque)
               
                
            efficiencies.append(efficiency)
            
            objective_function += 1 - efficiency
            if efficiency == 0:
                    objective_function +=10
            
        self.gearbox.efficiencies = efficiencies
        
        if x[1]>x[0]:
            objective_function += 10
        if x[2]>x[1]:
            objective_function += 10
            
        return objective_function


    def cond_init(self):
        x0=[]
        for interval in self.bounds:
            x0.append((interval[1]-interval[0])*float(npy.random.random(1))+interval[0])
        return x0
    
    def optimize(self, max_loops = 1000):
        
        valid = True
        count = 0
        list_gearbox=[]
        functionals=[]
        while valid and count < max_loops:
            x0 = self.cond_init()

            sol = minimize(self.objective, x0, bounds=self.bounds)
            count+=1
            if sol.fun < self.number_ratios and sol.success:
                self.gearbox.ratios = list(sol.x)
                list_gearbox.append(self.gearbox.copy())
                functionals.append(sol.fun)
        return [list_gearbox, functionals]
                