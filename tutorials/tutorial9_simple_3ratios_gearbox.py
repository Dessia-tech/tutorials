# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 13:30:58 2021

@author: wirajan
"""

from dessia_common import DessiaObject
from typing import List,Tuple
import numpy as npy
from scipy.optimize import minimize



class Data(DessiaObject):
    _standalone_in_db = True
    
    "Values used to determine the engine efficiency "
    def __init__(self, speed: List[Tuple[float, float]], torque: List[Tuple[float, float]], efficiency: List[float], name: str = ''): 
        self.speed = speed
        self.torque = torque
        self.efficiency = efficiency 
        
        DessiaObject.__init__(self,name=name)
      
class Motor(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, speed:float, torque:float, data : Data, name:str=''):
        # motor parameters
        self.speed = speed
        self.torque = torque
        self.data = data
        
        DessiaObject.__init__(self,name=name)
        
        
    def efficiency(self, speed: float, torque: float):
        efficiency = 0
        for i, spd in enumerate(self.data.speed):
            if speed > spd[0] and speed < spd[1]:
                if torque > self.data.torque[i][0] and torque < self.data.torque[i][1]:
                    efficiency = self.data.efficiency[i]
        return efficiency
        
class GearBox(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, motor: Motor, ratios = None, efficiencies = None, name: str = ''):
        self.motor = motor
        self.ratios = ratios
        self.efficiencies = efficiencies
        
        DessiaObject.__init__(self,name=name)

class GearBoxOptimizer(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, gearbox: GearBox, ratios_min_max: Tuple[float, float],
                 speeds = None, torques = None, number_ratios: int = 3, name: str = ''):
        self.gearbox = gearbox
        self.speeds = speeds
        self.torques = torques
        self.ratios_min_max = ratios_min_max
        self.number_ratios = number_ratios
        
        DessiaObject.__init__(self,name=name)
        
        
        bounds = []
        for ratio in range(self.number_ratios):
            bounds.append([ratios_min_max[0],ratios_min_max[1]])
        self.bounds = bounds
        
    def objective(self, x):
        " it's important to note that here  we use ratio as being defined by w_in/w_out"
        efficiencies = []
        objective_function = 0
        
        for i,(speed, torque) in enumerate(zip(self.speeds, self.torques)):
            ratio = x[i]
            motor_speed = speed * ratio
            motor_torque = torque / ratio
            efficiency = self.gearbox.motor.efficiency(motor_speed, motor_torque)
               
                
            efficiencies.append(efficiency)
            
            objective_function += 1 - efficiency
            if efficiency == 0:
                    objective_function += 10
            
        self.gearbox.efficiencies = efficiencies
        
        if x[1] > x[0]:
            objective_function += 10
        if x[2] > x[1]:
            objective_function += 10     
        return objective_function


    def cond_init(self):
        x0 = []
        for interval in self.bounds:
            x0.append((interval[1]-interval[0])*float(npy.random.random(1))+interval[0])
        return x0
    
    def optimize(self, max_loops = 1000):
        
        valid = True
        count = 0
        list_gearbox = []
        functionals = []
        while valid and count < max_loops:
            x0 = self.cond_init()

            sol = minimize(self.objective, x0, bounds=self.bounds)
            count += 1
            if sol.fun < self.number_ratios and sol.success:
                self.gearbox.ratios = list(sol.x)
                list_gearbox.append(self.gearbox.copy())
                functionals.append(sol.fun)
        return [list_gearbox, functionals]
                