# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 13:30:58 2021

@author: wirajan
"""

from dessia_common import DessiaObject
from typing import List,Tuple
import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import interp2d
from statistics import mean
import plot_data 
from plot_data.colors import *


    
    

class Efficiency_map(DessiaObject):
    _standalone_in_db = True
    
    "Values used to determine the engine efficiency "
    def __init__(self, engine_speeds: List[float], engine_torques: List[float], mass_flow_rate: List[float],
                 fuel_hv: float, name: str = ''): 
        self.engine_speeds = [i*np.pi/30 for i in engine_speeds] # in rad/s
        self.engine_torques = engine_torques   #in Nm 
        self.mass_flow_rate = mass_flow_rate
        self.fuel_hv = fuel_hv #fuel lower heating value in kWh/g

        DessiaObject.__init__(self,name=name)
        
        BSFC = []
        for i, engine_speed in enumerate(self.engine_speeds):
            list_bsfc = []
            for j, engine_torque in enumerate(self.engine_torques):
                bsfc = self.mass_flow_rate[i][j]*3600/(engine_speed*engine_torque/1000) # in g/kWh
                list_bsfc.append(bsfc)
            BSFC.append(list_bsfc)
        self.bsfc = BSFC
        
        efficiencies=[]
        for list_bsfc in BSFC:
            list_efficiencies=[]
            for bsfc in list_bsfc:
                efficiency = 1/(bsfc*self.fuel_hv)
                list_efficiencies.append(efficiency)
            efficiencies.append(list_efficiencies)
        self.efficiencies = efficiencies
   
class Engine(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, efficiency_map : Efficiency_map, engine_speeds: List[float] = None, engine_torques: List[float] = None , name:str=''):
        self.efficiency_map = efficiency_map
        self.engine_speeds = engine_speeds
        self.engine_torques = engine_torques
        
        DessiaObject.__init__(self,name=name)
    
    def efficiency(self, speed:float, torque:float):
        interpolate = interp2d(self.efficiency_map.engine_torques, self.efficiency_map.engine_speeds, self.efficiency_map.efficiencies)
        interpolate_efficiency = interpolate(torque, speed)
        return interpolate_efficiency[0]
    
    def consumption_efficiency(self, speed:float, torque: float):
        interpolate = interp2d(self.efficiency_map.engine_torques, self.efficiency_map.engine_speeds, self.efficiency_map.bsfc)
        interpolate_consumption_efficiency = interpolate(torque, speed)
        return interpolate_consumption_efficiency[0]

class WLTP_cycle(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, cycle_speeds: List[float], car_mass: float, tire_radius: float, dt: float = 1, name: str = ''):
        self.cycle_speeds = cycle_speeds #speed in km/h
        self.car_mass = car_mass
        self.tire_radius = tire_radius
        self.dt = dt
        DessiaObject.__init__(self,name=name)
        
        accelerations = []
        for i in range(len(self.cycle_speeds[:-1])):
            acceleration = (self.cycle_speeds[i + 1] - self.cycle_speeds[i]) * (5 / 18) / dt  # acceleration in m/s^2
            if acceleration < 0:
                acceleration *= -1
            accelerations.append(acceleration)
    
        cycle_torques=[]
        for acceleration in accelerations:
            torque = acceleration*car_mass*tire_radius/2                         #torque in Nm  
            cycle_torques.append(torque)
            
        self.cycle_torques = cycle_torques
        
class GearBox(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, engine: Engine, wltp_cycle: WLTP_cycle, ratios = None, fuel_consumptions: List[float] = None, gears: Tuple[float] = None, speed_ranges: List[float] = None, name: str = ''):
        self.engine = engine
        self.wltp_cycle = wltp_cycle
        self.ratios = ratios
        self.fuel_consumptions = fuel_consumptions
        self.gears = gears
        self.speed_ranges = speed_ranges
        
        DessiaObject.__init__(self,name=name)
        
    def gear_decision(self, x):
        max_torque_penaulty = 0
        fuel_consumptions = []
        gears = []
        ratios = []
        engine_speeds = []
        engine_torques = []
        
        for (cycle_speed, cycle_torque) in zip(self.wltp_cycle.cycle_speeds, self.wltp_cycle.cycle_torques):
            
            for i, speed_range in enumerate(self.speed_ranges):
                
                    if cycle_speed >= speed_range[0] and cycle_speed < speed_range[1]:
                        ratio = x[i]
                        engine_speed = (cycle_speed * 2.916302129) * ratio # here the constant stands for the speed unit transformation in rad/s
                        engine_torque = cycle_torque / ratio
                        if engine_torque > max(self.engine.efficiency_map.engine_torques):
                            max_torque_penaulty = 100
                        fuel_consumption_gpkwh = self.engine.consumption_efficiency(engine_speed, engine_torque)
                        gear = i+1
                        
            fuel_consumptions.append(fuel_consumption_gpkwh)
            gears.append(gear)
            ratios.append(ratio)
            engine_speeds.append(engine_speed*30/np.pi)
            engine_torques.append(engine_torque)
            
        cycle_average_consumption  = mean(fuel_consumptions)
        
        self.engine.engine_speeds = engine_speeds
        self.engine.engine_torques = engine_torques
        self.fuel_consumptions = fuel_consumptions
        self.gears = [gears, ratios]
                    
        return [cycle_average_consumption, max_torque_penaulty]

    # def gear_decision2(self, x, cycle_speed, cycle_torque):

class GearBoxOptimizer(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, gearbox: GearBox, wltp_cycle: WLTP_cycle, ratios_min_max: Tuple[float,float], name: str = ''):
        self.gearbox = gearbox
        self.wltp_cycle = wltp_cycle
        self.ratios_min_max = ratios_min_max
        
        
        DessiaObject.__init__(self,name=name)
        
        
        bounds=[]

        for ratio in range(len(self.gearbox.speed_ranges)):
            bounds.append([self.ratios_min_max[0],self.ratios_min_max[1]])
        self.bounds = bounds
        
        
        
    def objective(self, x):


        objective_function = 0
            
        gear_decision = self.gearbox.gear_decision(x)
          
        objective_function += gear_decision[0] + gear_decision[1]         
        
     
        return objective_function
    def const1(self,x):
        return x[0]-1.65*x[1]
    def const2(self,x):
        return x[1]-1.5*x[2]
    def const3(self,x):
        return x[2]-1.25*x[3]

    def cond_init(self):
        x0 = []
        for interval in self.bounds:
            x0.append((interval[1]-interval[0])*float(np.random.random(1))+interval[0])
        return x0
    
    def optimize(self, max_loops = 1000): 
        valid = True
        count = 0
        list_gearbox = []
        functionals = []
        solutions = []
        while valid and count < max_loops:
            x0 = self.cond_init()
            cons1 = {'type':'ineq', 'fun': self.const1}
            cons2 = {'type':'ineq', 'fun': self.const2}
            cons3 = {'type':'ineq', 'fun': self.const3}
            cons = [cons1, cons2, cons3]
            sol = minimize(self.objective, x0, bounds = self.bounds, constraints = cons)
            
            count += 1
            if sol.fun < max([j for i in self.gearbox.engine.efficiency_map.bsfc for j in i]) and sol.success:
                self.gearbox.ratios = list(sol.x)
                solutions.append(list(sol.x))
                functionals.append(sol.fun)
                list_gearbox.append(self.gearbox.copy())
                
        return [list_gearbox, functionals, solutions]
    

class Results(DessiaObject):
    def __init__(self, gearbox: GearBox, wltp_cycle: WLTP_cycle):
        self.gearbox = gearbox
        self.wltp_cycle = wltp_cycle
        
        
    def plot_data(self):
        points=[]
        for car_speed, wheel_torque, engine_speed, engine_torque, fuel_consuption in zip(self.wltp_cycle.cycle_speeds[:-1], self.wltp_cycle.cycle_torques ,self.gearbox.engine.engine_speeds,self.gearbox.engine.engine_torques, self.gearbox.fuel_consumptions):
            points.append({'car speed': car_speed,'wheel torque': wheel_torque,'engine speed': engine_speed, 'fuel consumtion':fuel_consuption})
            
        color_fill = LIGHTBLUE
        color_stroke = GREY
        point_style = plot_data.PointStyle(color_fill=color_fill, color_stroke=color_stroke)
        axis = plot_data.Axis()
        to_disp_attribute_names = ['fuel consumtion', 'car speed']
        tooltip = plot_data.Tooltip(to_disp_attribute_names=to_disp_attribute_names)
        objects = [plot_data.Scatter(tooltip=tooltip, to_disp_attribute_names=to_disp_attribute_names,
                                     point_style=point_style,
                                     elements=points, axis=axis)]

        edge_style = plot_data.EdgeStyle()
        rgbs = [[192, 11, 11], [14, 192, 11], [11, 11, 192]]
        objects.append(plot_data.ParallelPlot(elements=points,
                                              edge_style=edge_style,
                                              disposition='vertical',
                                              to_disp_attribute_names=['car speed', 'wheel torque', 'engine speed',
                                                                       'enigne torque','fuel consumtion'], rgbs=rgbs))
        
        list_colors = [BLUE, BROWN, RED, BLACK]           
        cycle_time = [i+1 for i in range(len(self.wltp_cycle.cycle_speeds[:-1]))]
        tooltip = plot_data.Tooltip(to_disp_attribute_names=['t', 'fuel consumption'])
        point_style = plot_data.PointStyle(color_fill=RED, color_stroke=BLACK)
        edge_style = plot_data.EdgeStyle(line_width=0.5 ,color_stroke = list_colors[0])
        
        elements = []
        datasets = []
        
        for i, gear in enumerate(self.gearbox.gears[0]):
            if i != 0:
                if self.gearbox.gears[0][i] != self.gearbox.gears[0][i-1]:
                    datasets.append(plot_data.Dataset(elements = elements, edge_style = edge_style, tooltip = tooltip, point_style = point_style))
                    elements = [{'t': cycle_time[i], 'fuel consumption': self.gearbox.fuel_consumptions[i]}]
                    for j in range(len(self.gearbox.ratios)):
                        if j + 1 == gear:
                            edge_style = plot_data.EdgeStyle(line_width=0.5 ,color_stroke = list_colors[j])
                else:
                    elements.append({'t': cycle_time[i], 'fuel consumption': self.gearbox.fuel_consumptions[i]})
                    
            if gear == self.gearbox.gears[0][-1]:
                datasets.append(plot_data.Dataset(elements = elements, edge_style = edge_style, tooltip = tooltip, point_style = point_style))
        graphs2d = plot_data.Graph2D(graphs = datasets, to_disp_attribute_names = ['t', 'fuel consumption'],)
        
        return graphs2d    
    
    
    
    
    
    
    
    
    
    
    
                
