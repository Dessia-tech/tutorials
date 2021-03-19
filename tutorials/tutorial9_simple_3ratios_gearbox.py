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
from plot_data.colors import GREY, BLACK, WHITE, LIGHTBLUE, RED, BLUE


    
    

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
        BSFC = self.bsfc
        for list_bsfc in BSFC:
            list_efficiencies=[]
            for bsfc in list_bsfc:
                efficiency = 1/(bsfc*self.fuel_hv)
                list_efficiencies.append(efficiency)
            efficiencies.append(list_efficiencies)
        self.efficiencies = efficiencies
   
class Motor(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, efficiency_map : Efficiency_map, engine_speeds = None, engine_torques = None, name:str=''):
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
    
class GearBox(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, motor: Motor, ratios = None, fuel_consumptions = None, gears= None, wltp = None, number_ratios:int=3, name: str = ''):
        self.motor = motor
        self.ratios = ratios
        self.number_ratios = number_ratios
        self.fuel_consumptions = fuel_consumptions 
        self.gears = gears
        self.wltp = wltp
        
        DessiaObject.__init__(self,name=name)
        
    def plot_data(self, cycle_speed, cycle_torques): 
        points=[]
        for car_speed, wheel_torque, engine_speed, engine_torque, fuel_consuption in zip(cycle_speed[:-1], cycle_torques ,self.motor.engine_speeds,self.motor.engine_torques, self.fuel_consumptions):
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
                                                                       'enigne torque','fuel consumtion'],
                                              rgbs=rgbs))
        
        
        # tooltip = plot_data.Tooltip(to_disp_attribute_names=['car speed', 'fuel consumption'])
        # point_style = plot_data.PointStyle(color_fill=RED, color_stroke=BLACK)
        # edge_style = plot_data.EdgeStyle(color_stroke=BLUE, dashline=[10, 5])
        # elements = []
        # for car_speed, fuel_consuption in zip(cycle_speed[:-1], self.fuel_consumptions):
        #     elements.append({'car speed': car_speed, 'fuel consumption': fuel_consuption})
        # objects = [plot_data.Dataset(elements=elements, name='car speed X fuel consumption', tooltip=tooltip, point_style=point_style,
        #                          edge_style=edge_style)]
        
        # tooltip = plot_data.Tooltip(to_disp_attribute_names=['wheel torque', 'fuel consumption'])
        # point_style = plot_data.PointStyle(color_fill=RED, color_stroke=BLACK)
        # edge_style = plot_data.EdgeStyle(color_stroke=BLUE, dashline=[10, 5])
        # elements = []
        # for wheel_torque, fuel_consuption in zip(cycle_torques, self.fuel_consumptions):
        #     elements.append({'wheel torque': wheel_torque, 'fuel consumption': fuel_consuption})
        # objects.append(plot_data.Dataset(elements=elements, name='wheel torque X fuel consumption', tooltip=tooltip, point_style=point_style,
        #                          edge_style=edge_style))
        
        # tooltip = plot_data.Tooltip(to_disp_attribute_names=['engine speed', 'fuel consumption'])
        # point_style = plot_data.PointStyle(color_fill=RED, color_stroke=BLACK)
        # edge_style = plot_data.EdgeStyle(color_stroke=BLUE, dashline=[10, 5])
        # elements = []
        # for engine_speed, fuel_consuption in zip(self.motor.engine_speeds, self.fuel_consumptions):
        #     elements.append({'engine speed': engine_speed, 'fuel consumption': fuel_consuption})
        # objects.append(plot_data.Dataset(elements=elements, name='engine speed X fuel consumption', tooltip=tooltip, point_style=point_style,
        #                          edge_style=edge_style))
        
        # tooltip = plot_data.Tooltip(to_disp_attribute_names=['engine torque', 'fuel consumption'])
        # point_style = plot_data.PointStyle(color_fill=RED, color_stroke=BLACK)
        # edge_style = plot_data.EdgeStyle(color_stroke=BLUE, dashline=[10, 5])
        # elements = []
        # for engine_torque, fuel_consuption in zip(self.motor.engine_torque, self.fuel_consumptions):
        #     elements.append({'engine torque': engine_torque, 'fuel consumption': fuel_consuption})
        # objects.append(plot_data.Dataset(elements=elements, name='engine torque X fuel consumption', tooltip=tooltip, point_style=point_style,
        #                          edge_style=edge_style))
        
        
        coords = [(0, 0), (500, 0)]
        sizes = [plot_data.Window(width=500, height=500),
                 plot_data.Window(width=500, height=500)]

        return plot_data.MultiplePlots(elements = points, plots=objects,
                                       sizes=sizes, coords=coords)

        
            

class GearBoxOptimizer(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, gearbox: GearBox, ratios_min_max: Tuple[float,float],
                 cycle_speeds: float = None, cycle_torques: float = None, speed_ranges:float = None,  name: str = ''):
        self.gearbox = gearbox
        self.cycle_speeds = [i*2.916302129 for i in cycle_speeds]                       #velocity in rad/s
        self.cycle_torques = cycle_torques
        self.ratios_min_max = ratios_min_max
        self.speed_ranges = [[i[0]*2.916302129,i[1]*2.916302129] for i in speed_ranges] # in rad/s
        
        DessiaObject.__init__(self,name=name)
        
        
        bounds=[]

        for ratio in range(len(self.speed_ranges)):
            bounds.append([self.ratios_min_max[0],self.ratios_min_max[1]])
        self.bounds = bounds
        
        
    def objective(self, x):
        "it's important to note that here  we use ratio as being defined by w_in/w_out"
       
        
        fuel_consumptions = []
        objective_function = 0
        gears = []
        ratios = []
        wltp = []
        engine_speeds = []
        engine_torques = []
        
        for (speed, torque) in zip(self.cycle_speeds, self.cycle_torques):

            # list_fuel_consumptions = []
            # list_motor_spd_trq = []
            for i, speed_range in enumerate(self.speed_ranges):
                if speed >= speed_range[0] and speed < speed_range[1]:
                    ratio = x[i]
                    motor_speed = speed * ratio
                    motor_torque = torque / ratio
                    if motor_torque > max(self.gearbox.motor.efficiency_map.engine_torques):
                        objective_function += 100
                    # efficiency = self.gearbox.motor.efficiency(motor_speed, motor_torque)   
                    fuel_consumption_gpkwh = self.gearbox.motor.consumption_efficiency(motor_speed, motor_torque)
                    gear = i+1
                    # ratio = 'ratio: ' + str(x[i])
                    # motor_speed ='motor speed in rpm: ' + str(motor_speed*30/np.pi)
                    # motor_torque = 'motor torque in Nm: ' + str(motor_torque)
  
            # objective_function += 1 - max(list_efficiencies)
            
            # for i,fuel_eff in enumerate(list_fuel_consumptions):
            #     if fuel_eff == min(list_fuel_consumptions):
            #         gear = 'gear'+ str(i+1)
            #         ratio = 'ratio: ' + str(x[i])
            #         motor_speed ='motor speed in rpm: ' + str(list_motor_spd_trq[i][0]*30/np.pi)
            #         motor_torque = 'motor torque in Nm: ' + str(list_motor_spd_trq[i][1])
                    
            engine_speeds.append(motor_speed*30/np.pi)
            engine_torques.append(motor_torque)
            # motor_speed_torque.append([motor_speed, motor_torque])       
            wltp.append(['wltp speed in km/h    : ' + str(speed/2.916302129), 'wltp torque in Nm: ' + str(torque)])  
            gears.append(gear)
            ratios.append(ratio)
            fuel_consumptions.append(fuel_consumption_gpkwh)
        
        objective_function += mean(fuel_consumptions)
            
        # self.gearbox.motor.speed_torque = motor_speed_torque
        self.gearbox.motor.engine_speeds = engine_speeds
        self.gearbox.motor.engine_torques = engine_torques
        self.gearbox.wltp = wltp
        self.gearbox.fuel_consumptions = fuel_consumptions
        self.gearbox.gears = [gears, ratios]
        
        # if x[1]>x[0]:
        #     objective_function += 100
        # if x[2]>x[1]:
        #     objective_function += 100
        
        # if x[0] == x[1]:
        #     objective_function += 1000
        # if x[1] == x[2]:
        #     objective_function += 1000
        # if x[2] == x[3]:
        #     objective_function += 1000
            
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
            if sol.fun < max([j for i in self.gearbox.motor.efficiency_map.bsfc for j in i]) and sol.success:
                self.gearbox.ratios = list(sol.x)
                solutions.append(list(sol.x))
                functionals.append(sol.fun)
                list_gearbox.append(self.gearbox.copy())
                
        return [list_gearbox, functionals, solutions]
    

        
        
        
        
    
    
# class Plot_data(DessiaObject):
#     _standalone_in_db = True
#     def __init__(self, gearbox_optimizer: GearBoxOptimizer, name: str = ''):
#          self.gearbox_optimizer = gearbox_optimizer
#          DessiaObject.__init__(self,name=name)
         
    
    
    
    
    
    
    
    
    
    
                