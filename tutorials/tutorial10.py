# -*- coding: utf-8 -*-
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
import dectree as dt
import copy
    
    

class EfficiencyMap(DessiaObject):
    _standalone_in_db = False
    
    """
    Build the engine map and then determine its efficiency 
    """
    def __init__(self, engine_speeds: List[float], engine_torques: List[float], mass_flow_rate: List[Tuple[float, float]],
                 fuel_hv: float, name: str = ''): 
        self.engine_speeds = engine_speeds                                      # in rad/s
        self.engine_torques = engine_torques                                    #in Nm 
        self.mass_flow_rate = mass_flow_rate
        self.fuel_hv = fuel_hv                                                  #fuel lower heating value in J/kg

        DessiaObject.__init__(self,name=name)
        
        BSFC = []
        for i, engine_speed in enumerate(self.engine_speeds):
            list_bsfc = []
            for j, engine_torque in enumerate(self.engine_torques):
                bsfc = self.mass_flow_rate[i][j]/(engine_speed*engine_torque)   # in kg/J
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
        
class WLTPCycle(DessiaObject):
    _standalone_in_db = False
    """
    WLTP cycle paremeters and wheel torque calculations
    """
    def __init__(self, cycle_speeds: List[float], car_mass: float, tire_radius: float, dt: float = 1, name: str = ''):
        self.cycle_speeds = cycle_speeds
        self.car_mass = car_mass
        self.tire_radius = tire_radius
        self.dt = dt
        DessiaObject.__init__(self,name=name)
        
        accelerations = []
        for i in range(len(self.cycle_speeds[:-1])):
            acceleration = (self.cycle_speeds[i + 1] - self.cycle_speeds[i]) / dt   # acceleration in m/s^2
            if acceleration < 0:
                acceleration *= -1
            accelerations.append(acceleration)
    
        cycle_torques=[]
        for acceleration in accelerations:
            torque = acceleration*car_mass*tire_radius/2                            #torque in Nm  
            cycle_torques.append(torque)
            
        self.cycle_torques = cycle_torques 
        
class Engine(DessiaObject):
    _standalone_in_db = True

    def __init__(self, efficiency_map : EfficiencyMap, setpoint_speed: float, setpoint_torque: float, name:str=''):
        self.efficiency_map = efficiency_map
        self.setpoint_speed = setpoint_speed
        self.setpoint_torque = setpoint_torque

        DessiaObject.__init__(self,name=name)
    
    def efficiency(self, speed:float, torque:float):
        interpolate = interp2d(self.efficiency_map.engine_torques, self.efficiency_map.engine_speeds, self.efficiency_map.efficiencies)
        interpolate_efficiency = interpolate(torque, speed)
        return interpolate_efficiency[0]
    
    def consumption_efficiency(self, speed:float, torque: float):
        interpolate = interp2d(self.efficiency_map.engine_torques, self.efficiency_map.engine_speeds, self.efficiency_map.bsfc)
        interpolate_consumption_efficiency = interpolate(torque, speed)
        return float(interpolate_consumption_efficiency[0])
  
class GearBox(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, engine: Engine, speed_ranges: List[Tuple[float, float]], ratios: List[float] = None, name: str = ''):
        self.engine = engine
        self.speed_ranges = speed_ranges
        self.ratios = ratios
        self.gear_connections = []
        DessiaObject.__init__(self,name=name)
        
    def update(self, x):
        ratios = []
        for i in range(len(x)):
            if i == 0:
                ratio = float(x[0])
                ratios.append(ratio)
            else:
                ratio *= float(x[i])
                ratios.append(ratio)
        self.ratios = ratios
        
    def gear_choice(self, cycle_speed, cycle_torque):
        fuel_consumption_gpkwh = 0
        engine_speed = 0
        engine_torque = 0
        gear = 0
        ratio = 0
  
        if cycle_speed == 0:
            engine_speed = self.engine.setpoint_speed
            engine_torque = self.engine.setpoint_torque
            fuel_consumption_gpkwh = self.engine.consumption_efficiency(engine_speed, engine_torque)
            gear = 0
            ratio = 0
        else:
            list_ratio = []
            list_gear = []
            list_fuel_c = []
            list_torque = []
            list_speed = []
            for i, speed_range in enumerate(self.speed_ranges):
                if cycle_speed  >= speed_range[0] and cycle_speed  < speed_range[1]:  
                    ratio = self.ratios[i]
                    engine_speed = cycle_speed * ratio 
                    engine_torque = cycle_torque / ratio  
                    fuel_consumption_gpkwh = self.engine.consumption_efficiency(engine_speed, engine_torque)
                    gear = i + 1
                    list_ratio.append(ratio)
                    list_gear.append(gear)
                    list_fuel_c.append(fuel_consumption_gpkwh)
                    list_speed.append(engine_speed)
                    list_torque.append(engine_torque)
            
            fuel_consumption_gpkwh = min(list_fuel_c)
            ratio = list_ratio[list_fuel_c.index(fuel_consumption_gpkwh)]
            gear = list_gear[list_fuel_c.index(fuel_consumption_gpkwh)]
            engine_speed = list_speed[list_fuel_c.index(fuel_consumption_gpkwh)]
            engine_torque = list_torque[list_fuel_c.index(fuel_consumption_gpkwh)]
                    
        return [ gear, ratio, fuel_consumption_gpkwh, engine_speed, engine_torque]

class GearBoxResults(DessiaObject): 
    _standalone_in_db = True
    
    def __init__(self, gearbox: GearBox, wltp_cycle: WLTPCycle, engine_speeds: List[float], engine_torques: List[float], fuel_consumptions:List[float],
                 gears: List[float], ratios:List[float], average_fuel_consumption:float, name: str = ''):
        self.gearbox = gearbox
        self.wltp_cycle = wltp_cycle
        self.engine_speeds =engine_speeds
        self.engine_torques = engine_torques
        self.fuel_consumptions = fuel_consumptions
        self.gears = gears
        self.ratios = ratios
        self.average_fuel_consumption = average_fuel_consumption
        DessiaObject.__init__(self,name=name)
        
        self.average_engine_speed = mean(self.engine_speeds)
        self.average_engine_torque = mean(self.engine_torques)
        self.ratio_min = min(self.gearbox.ratios)
        self.ratio_max = max(self.gearbox.ratios)
        self.average_ratio = mean(self.gearbox.ratios)
        
 
    def plot_data(self):
        
        cycle_time = [i+1 for i in range(len(self.wltp_cycle.cycle_speeds[:-1]))]
        points=[]
        for car_speed, wheel_torque, engine_speed, engine_torque, fuel_consumption, time, gear in zip(self.wltp_cycle.cycle_speeds[:-1], self.wltp_cycle.cycle_torques ,self.engine_speeds,self.engine_torques, self.fuel_consumptions, cycle_time, self.gears):
            points.append({'c_s': car_speed,'whl_t': wheel_torque,'w_e': engine_speed,'t_e': engine_torque, 'f_cons (g/kWh)':fuel_consumption*3.6e9, 'time': time, 'gear': gear})

        color_fill = LIGHTBLUE
        color_stroke = GREY
        point_style = plot_data.PointStyle(color_fill=color_fill, color_stroke=color_stroke)
        axis = plot_data.Axis()
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        to_disp_attribute_names = ['c_s', 'f_cons (g/kWh)']
        tooltip = plot_data.Tooltip(to_disp_attribute_names=to_disp_attribute_names,)
        objects = [plot_data.Scatter(tooltip=tooltip, to_disp_attribute_names=to_disp_attribute_names,
                                     point_style=point_style,
                                     elements=points, axis=axis)]
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        to_disp_attribute_names = ['whl_t', 'f_cons (g/kWh)']
        tooltip = plot_data.Tooltip(to_disp_attribute_names=to_disp_attribute_names)
        objects.append(plot_data.Scatter(tooltip=tooltip, to_disp_attribute_names=to_disp_attribute_names,
                                      point_style=point_style,
                                      elements=points, axis=axis))
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        edge_style = plot_data.EdgeStyle()
        rgbs = [[192, 11, 11], [14, 192, 11], [11, 11, 192]]
        objects.append(plot_data.ParallelPlot(elements=points, edge_style=edge_style,
                                              disposition='vertical',to_disp_attribute_names = ['w_e','t_e','f_cons (g/kWh)'],
                                              rgbs=rgbs))

        coords = [(0, 0), (500, 0),(1000,0)]
        sizes = [plot_data.Window(width = 500, height = 500),
                 plot_data.Window(width = 500, height = 500),
                 plot_data.Window(width = 500, height = 500)]
        multiplot = plot_data.MultiplePlots(elements=points, plots=objects,
                                       sizes=sizes, coords=coords)
        
        list_colors = [BLUE, BROWN, GREEN, BLACK]
        graphs2d = []
        point_style = plot_data.PointStyle(color_fill=RED, color_stroke=BLACK, size = 1)
        
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        tooltip = plot_data.Tooltip(to_disp_attribute_names=['sec', 'gear'])
        edge_style = plot_data.EdgeStyle(line_width=0.5 ,color_stroke = list_colors[0])
        elements = []
        for i, gear in enumerate(self.gears):
            elements.append({'sec': cycle_time[i], 'gear': gear})         
        dataset = plot_data.Dataset(elements = elements, edge_style = edge_style, tooltip = tooltip, point_style = point_style)
        graphs2d.append(plot_data.Graph2D(graphs = [dataset], to_disp_attribute_names = ['sec', 'gear']))
        
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

        tooltip = plot_data.Tooltip(to_disp_attribute_names=['sec', 'f_cons (g/kWh)'])
        edge_style = plot_data.EdgeStyle(line_width=0.5 ,color_stroke = list_colors[0])
        elements = []
        for i, gear in enumerate(self.gears):
            elements.append({'sec': cycle_time[i], 'f_cons (g/kWh)': self.fuel_consumptions[i]*3.6e9})         
        dataset = plot_data.Dataset(elements = elements, edge_style = edge_style, tooltip = tooltip, point_style = point_style)
        graphs2d.append(plot_data.Graph2D(graphs = [dataset], to_disp_attribute_names = ['sec', 'f_cons (g/kWh)']))
        
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
         
        tooltip  = plot_data.Tooltip(to_disp_attribute_names=['sec', 'w_e'])
        edge_style = plot_data.EdgeStyle(line_width=0.5 ,color_stroke = list_colors[2])
        elements = []
        for i, torque in enumerate(self.wltp_cycle.cycle_torques):
            elements.append({'sec':cycle_time[i], 'w_e':self.engine_speeds[i]})
        dataset = plot_data.Dataset(elements = elements, edge_style = edge_style, tooltip = tooltip, point_style = point_style)
        graphs2d.append(plot_data.Graph2D(graphs = [dataset], to_disp_attribute_names = ['sec', 'w_e']))
        
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        
        tooltip  = plot_data.Tooltip(to_disp_attribute_names=['sec', 'w_t'])
        edge_style = plot_data.EdgeStyle(line_width=0.5 ,color_stroke = list_colors[3])
        elements = []
        for i, torque in enumerate(self.wltp_cycle.cycle_torques):
            elements.append({'sec':cycle_time[i], 'w_t':self.engine_torques[i]})
        dataset = plot_data.Dataset(elements = elements, edge_style = edge_style, tooltip = tooltip, point_style = point_style)
        graphs2d.append(plot_data.Graph2D(graphs = [dataset], to_disp_attribute_names = ['sec', 'w_t']))

        coords = [(0, 0), (0,187.5), (0,375), (0,562.5)]
        sizes = [plot_data.Window(width=1500, height=187.5),
                 plot_data.Window(width=1500, height=187.5),
                 plot_data.Window(width=1500, height=187.5),
                 plot_data.Window(width=1500, height=187.5)]
        multiplot2 = plot_data.MultiplePlots(elements=points, plots=graphs2d,
                                       sizes=sizes, coords=coords)
       
        return [multiplot, multiplot2]
    
class GearBoxOptimizer(DessiaObject):
    _standalone_in_db = True
    
    def __init__(self, gearbox: GearBox, wltp_cycle: WLTPCycle, first_gear_ratio_min_max: Tuple[float,float], coeff_between_gears: List[Tuple[float, float]] = None, name: str = ''):
        self.gearbox = gearbox
        self.wltp_cycle = wltp_cycle
        self.coeff_between_gears = coeff_between_gears
        self.first_gear_ratio_min_max = first_gear_ratio_min_max
        DessiaObject.__init__(self,name=name)
        
        if self.coeff_between_gears == None:
            self.coeff_between_gears = (len(self.gearbox.speed_ranges)-1)*[[0.5,1]]
 
        bounds=[]
        for i in range(len(self.gearbox.speed_ranges)):
            if i == 0:
                bounds.append([self.first_gear_ratio_min_max[0],self.first_gear_ratio_min_max[1]])
            else: 
                bounds.append([self.coeff_between_gears[i-1][0], self.coeff_between_gears[i-1][1]])
        self.bounds = bounds
  
    def objective(self, x):
        self.update(x)
        objective_function = 0
        
        objective_function += mean(self.fuel_consumptions) 
        
        for engine_torque in self.engine_torques:
            if engine_torque > max(self.gearbox.engine.efficiency_map.engine_torques):
                objective_function += 1000

        return objective_function    
    
    def update(self, x):
        self.gearbox.update(x)
        
        fuel_consumptions = []
        gears = []
        ratios = []
        engine_speeds = []
        engine_torques = []
        
        for (cycle_speed, cycle_torque) in zip(self.wltp_cycle.cycle_speeds, self.wltp_cycle.cycle_torques): 
            cycle_speed = cycle_speed*2/self.wltp_cycle.tire_radius
            gear_choice = self.gearbox.gear_choice(cycle_speed, cycle_torque)
            gears.append(gear_choice[0])
            ratios.append(gear_choice[1])
            fuel_consumptions.append(gear_choice[2])
            engine_speeds.append(gear_choice[3])
            engine_torques.append(gear_choice[4])
           
        
        self.engine_speeds = engine_speeds
        self.engine_torques = engine_torques
        self.gears = gears
        self.ratios = ratios
        self.fuel_consumptions = fuel_consumptions

    def cond_init(self):
        x0 = []
        for interval in self.bounds:
                x0.append((interval[1]-interval[0])*float(np.random.random(1))+interval[0])
        return x0
    
    def optimize(self, max_loops:int = 1000): 
        valid = True
        count = 0
        list_gearbox_results = []
        
        while valid and count < max_loops:
            x0 = self.cond_init()
            self.update(x0)
            sol = minimize(self.objective, x0, bounds = self.bounds)
            count += 1
            if sol.fun < max([j for i in self.gearbox.engine.efficiency_map.bsfc for j in i]) and sol.success:
                self.average_fuel_consumption = float(sol.fun)
                self.update(list(sol.x))
                gearbox = self.gearbox.copy()
                gearbox.ratios = self.gearbox.ratios
                gearbox_results = GearBoxResults(gearbox, self.wltp_cycle, self.engine_speeds,  self.engine_torques,  self.fuel_consumptions,  self.gears, self.ratios, self.average_fuel_consumption) 
                list_gearbox_results.append(gearbox_results)
                
        return list_gearbox_results
    
class GearBoxGenerator(DessiaObject):
    
    
    def __init__(self, gearbox: GearBox, max_number_meshes: int, max_number_shafts: int = 3, number_connections: int = 3 ,name = ''):
        self.gearbox = gearbox
        self.max_number_shafts = max_number_shafts
        self.max_number_meshes = max_number_gears
        self.number_connections = number_connections

        DessiaObject.__init__(self,name=name)
    
    def generate(self):
        
        list_node = []
        # list_gear = []
        # gearbox = self.gearbox
       
        for i in range(self.max_number_shafts + self.max_number_meshes):
            list_node.append(self.number_connections)
            # list_gear.append(i + 1)
        
        tree = dt.RegularDecisionTree(list_node)
        list_gearbox = []
        list_valid_nodes = []
        
        
        while not tree.finished:
             valid = True
             node = tree.current_node
             connections = []
             connections.append(node[-1])
             
             # gearbox.gear_connections[len(node) - 1] = node[-1]
             
             # if len(node) <= len(list_gear)/2 + 1:
             #     if node[-1] != 0:
             #         valid  = False
             # else:
             #     if node[-1] == 2:
             #         valid = False
             
             # if len(node)==len(list_gear) and valid:
             #     list_connections 
             #     list_gearbox.append(copy.deepcopy(gearbox))
             #     list_valid_nodes.append(node)
                 
             tree.NextNode(valid)
             
        return list_gearbox, list_valid_nodes
             
             du coup, la façon dont on  determine les connections entre un seront determiné comment? 
        
        
        
        
        


        
    
    
    
    
    
    
    
    
    
    