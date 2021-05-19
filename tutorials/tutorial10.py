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
import plot_data.graph 
import copy
import networkx as nx
import networkx.algorithms.isomorphism as iso
from powertransmission.architecture import Shaft
from collections import Counter
from itertools import product
import matplotlib.pyplot as plt

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
    # _non_serializable_attributes = ['graph']
    
    def __init__(self, engine: Engine, speed_ranges: List[Tuple[float, float]], ratios: List[float] = None, graph: nx.Graph=None, name: str = ''):
        self.engine = engine
        self.speed_ranges = speed_ranges
        self.ratios = ratios
        # self.gearbox_connections = {}
        DessiaObject.__init__(self,name=name)
        # self._utd_graph = False
        self.graph = graph
        self.average_path_length = 0
        self.average_clutch_distance = 0
        
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
    
    def update_gb_graph(self, graph):
        self.graph = graph
        self.average_path_length = graph.graph['Average length path']
        self.average_clutch_distance = graph.graph['Average distance clutch-input']
       
    
    # def _get_graph(self):
    #     if not self._utd_graph:
    #         self._cached_graph = self.gearbox_graph
    #         self._utd_graph = True
    #     return self._cached_graph

    # graph = property(_get_graph)
    
    def plot_data(self):
        gearbox_graph = self.graph
        gears = []
        shafts = []
        S_G = []
        for node in gearbox_graph.nodes():
            if 'S' in node and 'G' in node:
                gearbox_graph.nodes()[node]['color'] = 'rgb(169,169,169)'
                gearbox_graph.nodes()[node]['shape'] = 'o'
                gearbox_graph.nodes()[node]['name'] = node
                S_G.append(node)
            elif 'S' in node and 'G' not in node:
                gearbox_graph.nodes()[node]['color'] = 'rgb(195,230,252)'
                gearbox_graph.nodes()[node]['shape'] = 'o'
                gearbox_graph.nodes()[node]['name'] = node
                shafts.append(node)
            else:
                gearbox_graph.nodes()[node]['color'] = 'rgb(19,240,240)'
                gearbox_graph.nodes()[node]['shape'] = 's'
                gearbox_graph.nodes()[node]['name'] = node
                gears.append(node)
                
        edges = []
        edges_clutch =[]
        for edge in gearbox_graph.edges():
            if gearbox_graph.edges()[edge]:
                gearbox_graph.edges()[edge]['color'] = 'rgb(247,0,0)'
                gearbox_graph.edges()[edge]['width'] = 10
                edges_clutch.append(edge)
            else:
                gearbox_graph.edges()[edge]['color'] = 'rgb(0,0,0)'
                gearbox_graph.edges()[edge]['width'] = 5
                edges.append(edge)
        return [plot_data.graph.NetworkxGraph(gearbox_graph)]
    
    
    def to_dict(self, subobjects_id = {}):
        """
        Export dictionary
        """
        d = {}
        d['engine'] = self.engine.to_dict()
        d['speed_ranges'] = self.speed_ranges
        d['ratios'] = self.ratios
        d['average_path_length'] = self.average_path_length
        d['average_clutch_distance'] = self.average_clutch_distance
        d['graph'] = nx.readwrite.json_graph.node_link_data(self.graph)
        d['name'] = self.name
        d['object_class'] = 'tutorials.tutorial10.GearBox'
        
        return d
    @classmethod
    def dict_to_object(cls, d):
        obj = cls(engine = Engine.dict_to_object(d['engine']),
                  speed_ranges =  d['speed_ranges'],
                  ratios = d['ratios'], 
                  # average_path_length =  d['average_path_length'],
                  # average_clutch_distance = d['average_clutch_distance'],
                  graph = nx.readwrite.json_graph.node_link_graph(d['graph']),
                  name = d['name'],
                  # object_class = d['object_class']
                  )
        return obj

        
         

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
    
    
    def __init__(self, gearbox: GearBox, number_inputs:int, number_shaft_assemblies: int,   max_number_gears: int, connections: List[str] = ['existent', 'inexistent'] ,name:str = ''):
        self.gearbox = gearbox
        self.number_inputs = number_inputs
        self.number_shaft_assemblies = number_shaft_assemblies
       
        self.max_number_gears = max_number_gears
        self.connections = connections
        DessiaObject.__init__(self,name=name)
        
    def generate_connections(self):
        list_node = []
        connections = []
        list_dict_connections = []
        dict_connections = {}
        for i in range(self.number_shaft_assemblies):
            for j in range(self.number_shaft_assemblies):
                if i < j:
                    connections.append((i+1, j+1))
        # print(connections)
        for gear in range(self.max_number_gears):
            list_node.append(len(connections))
            
            
        tree = dt.RegularDecisionTree(list_node)
        while not tree.finished:
              valid = True
              node = tree.current_node
              if len(node) >  1:
                  
                  if connections[node[-1]][0] != connections[node[-2]][0]:
                      if connections[node[-1]][0] != connections[node[-2]][1]:
                          valid = False      
              if len(node) == self.max_number_gears and valid:
                  for i_node, nd in enumerate(node):
                      dict_connections['G' + str(i_node+1)] = connections[nd]
                  list_dict_connections.append(copy.copy(dict_connections))
              tree.NextNode(valid)
        return list_dict_connections
    
    def generate_paths(self):
        list_gearbox_connections = self.generate_connections()
        list_gearbox_graphs = []
        list_paths = []
        list_paths_edges = []
        list_counter_paths_between_2shafts = []
        list_dict_connections = []
        for gearbox_connections in list_gearbox_connections:
            # gearbox_graph = nx.DiGraph()
            gearbox_graph = nx.Graph()
            for gearbox_connection in gearbox_connections:
                gearbox_graph.add_edge('S'+str(gearbox_connections[gearbox_connection][0]), gearbox_connection)
                gearbox_graph.add_edge(gearbox_connection,'S'+str(gearbox_connections[gearbox_connection][1]))
        
            input_shaft = min([shaft for gearbox_connection in gearbox_connections.values() for shaft in gearbox_connection])
            output_shaft = max([shaft for gearbox_connection in gearbox_connections.values() for shaft in gearbox_connection])
            for shaft in range(self.number_shaft_assemblies):
                for node in gearbox_graph.nodes():
                    if node == 'S'+str(input_shaft):
                        gearbox_graph.nodes()[node]['Node Type'] = 'Input Shaft'
                    elif node == 'S'+str(output_shaft):
                        gearbox_graph.nodes()[node]['Node Type'] = 'Output Shaft'
                    elif 'S' in node:
                        gearbox_graph.nodes()[node]['Node Type'] = 'Shaft'
                    else:
                        gearbox_graph.nodes()[node]['Node Type'] = 'Gear'
            paths = []
            count = 0
            average_lengths = []  
            for path in nx.all_simple_paths(gearbox_graph, 'S'+str(input_shaft), 'S'+str(output_shaft)):
                paths.append(path)
                average_lengths.append(len(path))
                count += 1
            paths_edges = []
            for path in map(nx.utils.pairwise, paths):
                paths_edges.append(list(path))
                
            if count == len(self.gearbox.speed_ranges):
                valid = True
                
                for node in gearbox_graph.nodes(): 
                    if node not in [path_node for path in paths for path_node in path]:
                        valid = False

                # graph_paths_nodes = [node for path in paths for node in path]
                # counter_paths_between_2shafts = {}
                # for i in range(self.number_shaft_assemblies):
                #     for j in range(self.number_shaft_assemblies):
                #         if i < j:
                #             if 'S'+str(i+1) in graph_paths_nodes and 'S'+str(j+1) in graph_paths_nodes:
                #                 counter_paths_between_2shafts['S'+str(i+1)+'-S'+str(j+1)] = (len(list(nx.all_simple_paths(gearbox_graph, 'S'+str(i+1), 'S'+str(j+1)))),\
                #                                                                                dict(Counter([len(path) for path  in nx.all_simple_paths(gearbox_graph, 'S'+str(i+1), 'S'+str(j+1))])))
 
                # if list(counter_paths_between_2shafts.values()) in [list(counter.values()) for counter in list_counter_paths_between_2shafts]:
                #     valid = False
                
                
                for graph in list_gearbox_graphs:
                    node_match = iso.categorical_node_match('Node Type', 'Shaft')
                    if nx.is_isomorphic(gearbox_graph, graph, node_match= node_match):
                        valid = False

                if valid:
                    gearbox_graph.graph['Average length path'] = mean(average_lengths)
                    list_gearbox_graphs.append(gearbox_graph)
                    list_paths.append(paths)
                    list_paths_edges.append(paths_edges)
                    # list_counter_paths_between_2shafts.append(counter_paths_between_2shafts)
                    list_dict_connections.append(gearbox_connections)
        
        return list_gearbox_graphs, list_paths, list_paths_edges, list_counter_paths_between_2shafts,list_dict_connections
    
    def clutch_analisys(self):
        new_list_gearbox_graphs = []
        list_clutch_combinations = []
        list_cycles = []
        list_dict_clutch_connections = []
        list_gearbox_graphs = self.generate_paths()[0]
        for graph in list_gearbox_graphs:
            cycles = nx.cycle_basis(graph)
            list_cycles.append(cycles)
            list_cycle_shafts = []
            
            for cycle in cycles:
                cycle_shafts = []
                for node in cycle:
                    if 'S' in node:
                        cycle_shafts.append(node)
                list_cycle_shafts.append(cycle_shafts)
            clutch_combinations = list(product(list_cycle_shafts[0], list_cycle_shafts[1]))
            list_clutch_combinations.append(clutch_combinations)
            for clutch_combination in clutch_combinations:
                graph_copy = copy.deepcopy(graph)
                dict_clutch_connections = {}
                for i_cycle, cycle in enumerate(cycles):
                    # if 'G' in cycle[0]:
                    for i_node, node in enumerate(cycle):
                        if clutch_combination[i_cycle] == node:
                        
                            
                            if clutch_combination[i_cycle] == cycle[-1]:
                                dict_clutch_connections[i_cycle + 1] = (cycle[0], cycle[i_node-1])
                                graph_copy.nodes()[node]['Clutch'] = True
                            else:
                                dict_clutch_connections[i_cycle + 1] = (cycle[i_node+1], cycle[i_node-1])
                                graph_copy.nodes()[node]['Clutch'] = True
                      
                list_dict_clutch_connections.append(dict_clutch_connections)
                new_list_gearbox_graphs.append(graph_copy)
        
        return new_list_gearbox_graphs, list_dict_clutch_connections, list_clutch_combinations, list_cycles
    
    def generate(self):
        list_gearbox_solutions = []
        clutch_analisys = self.clutch_analisys()
        clutch_gearbox_graphs = clutch_analisys[0]
        list_clutch_connections = clutch_analisys[1]
        list_clutch_combinations = [clutch_combination for clutch_combinations in clutch_analisys[2] for clutch_combination in clutch_combinations]
        list_clutch_gearbox_graphs = []
        # list_average_lengths = []
        for i_graph, graph in enumerate(clutch_gearbox_graphs):
            graph_copy = copy.deepcopy(graph)
            clutch_connections = list_clutch_connections[i_graph]
            if list_clutch_connections[i_graph][1] ==  list_clutch_connections[i_graph][2]:
                print(list_clutch_connections[i_graph][1],list_clutch_connections[i_graph][2])
                continue
            for node in graph.nodes():
                if 'Clutch' in list(graph.nodes()[node].keys()):
                    for edge in graph.edges():
                                
                        if node in edge:
                            
                            clutch_link_values = [value for values in clutch_connections.values() for value in values]
                            if edge[0] in clutch_link_values or edge[1] in clutch_link_values:
                                graph_copy.remove_edge(edge[0], edge[1])
                                if 'S' in edge[0]:
                                    graph_copy.add_edge(edge[1],edge[0]+'-'+edge[1]) 
                                    graph_copy.add_edge(edge[0], edge[0]+'-'+edge[1])
                                else:
                                    graph_copy.add_edge(edge[0],edge[1]+'-'+edge[0]) 
                                    graph_copy.add_edge(edge[1], edge[1]+'-'+edge[0])
            clutches = []
            for node in graph_copy.nodes():
                if graph_copy.nodes()[node]:
                    if graph_copy.nodes()[node]['Node Type'] == 'Input Shaft':
                        input_shaft = node
                    if graph_copy.nodes()[node]['Node Type'] == 'Output Shaft':
                        output_shaft = node
                    if 'Clutch' in list(graph.nodes()[node].keys()):
                        clutches.append(node)
            paths = nx.all_simple_paths(graph_copy, input_shaft, output_shaft) 
            valid = True  
            for path in paths:
                if not any(('S' in node and 'G' in node) for node in path):
                    valid = False
            clutch_average_path_length = []
            for clutch in clutches:
                clutch_average_path_length.append(nx.shortest_path_length(graph_copy, input_shaft, clutch))
                 
            for i_shaft, shaft in enumerate(list_clutch_combinations[i_graph]):
                graph_copy.add_edges_from([(shaft+'-'+ clutch_connections[i_shaft+1][0], shaft+'-'+ clutch_connections[i_shaft+1][1],{'Clucth': True})])
            if valid:
                graph_copy.graph['Average distance clutch-input'] = mean(clutch_average_path_length)
                
                gearbox = self.gearbox.copy()
                gearbox.update_gb_graph(graph_copy)
                list_gearbox_solutions.append(gearbox)
                list_clutch_gearbox_graphs.append(graph_copy)
                
            
        return list_gearbox_solutions
    # , list_clutch_gearbox_graphs
    
    def draw_graph(self, graphs_list: List[nx.Graph], max_number_graphs:int = None):
        
        for i, graph in enumerate(graphs_list):
            plt.figure()
            gears = []
            shafts = []
            S_G = []
            for node in graph.nodes():
                for node in graph.nodes():
                    if 'S' in node and 'G' in node:
                        S_G.append(node)
                    elif 'S' in node and 'G' not in node:
                        shafts.append(node)
                    else:
                        gears.append(node)
            edges = []
            edges_clutch =[]
            for edge in graph.edges():
                if graph.edges()[edge]:
                    edges_clutch.append(edge)
                else:
                    edges.append(edge)
            pos = nx.kamada_kawai_layout(graph)
            
            nx.draw_networkx_nodes(graph, pos, shafts, node_color='skyblue', node_size=1000)
            nx.draw_networkx_nodes(graph, pos, S_G, node_color='grey', node_size=500)
            nx.draw_networkx_nodes(graph, pos, gears, node_shape = 's', node_color='steelblue', node_size=1000)
            nx.draw_networkx_edges(graph, pos, edges_clutch,edge_color='red', width= 3)
            nx.draw_networkx_edges(graph, pos, edges)
            labels = {element: element for element in  shafts + S_G + gears}
            nx.draw_networkx_labels(graph, pos, labels=labels)
            if max_number_graphs is not None:
                if i >= max_number_graphs:
                    break
                                            
                                            
                
            
                
                      
                  
        # print(connections)
    
    # def gearbox_graph(self):
    #     gearbox_graph = nx.Graph()
    
    #     for n_gear in range(self.max_number_gears):
    #         for n_shaft in range(self.max_number_shafts):
    #                 gearbox_graph.add_edge('G' + str(n_gear+1), 'S' + str(n_shaft+1))
    #             # if n_gear == n_shaft and n_gear+1 <= self.number_inputs:    
    #             #     gearbox_graph.add_edge('G' + str(n_gear+1), 'S' + str(n_shaft+1))
    #             # else:
    #             #     if n_shaft+1 > self.number_inputs:
    #             #         gearbox_graph.add_edge('G' + str(n_gear+1), 'S' + str(n_shaft+1))
    #     return gearbox_graph
   
            
    # def connections_decision_tree(self):
    #     list_node = []
    #     list_edges = []
    #     # gearbox = self.gearbox.copy()
    #     gearbox_graph = self.gearbox_graph()
    #     dict_connections = {}
    #     list_dict_connections = []
    #     for edge in gearbox_graph.edges():
    #         list_node.append(len(self.connections))
    #         list_edges.append(edge)
    #     edges = []
    #     for gear in range(self.max_number_gears):
    #         for shaft in range(self.max_number_shafts):
    #             if ('G' + str(gear+1), 'S' + str(shaft+1)) in list_edges: 
    #                 edges.append(('G' + str(gear+1), 'S' + str(shaft+1)))
    #             if ('S' + str(shaft+1), 'G' + str(gear+1)) in list_edges:
    #                 edges.append(('S' + str(shaft+1), 'G' + str(gear+1)))
    #     # for connection in edges:
    #     #     dict_connections[connection] = 0 
                
    #     print(edges)
    #     print(list_edges)
        
        
    #     tree = dt.RegularDecisionTree(list_node)
    #     list_gearbox = []
    #     list_nodes = []
    #     while not tree.finished:
    #           valid = True
    #           node = tree.current_node
    #           if not len(node)%self.max_number_shafts == 0: 
    #               if node[self.max_number_shafts*int(len(node)/self.max_number_shafts):].count(0) > 2:
    #                 valid = False
    #           else:
    #               if node[-self.max_number_shafts:].count(self.connections.index('inexistent')) < self.max_number_shafts:
    #                   if node[-self.max_number_shafts:].count(self.connections.index('inexistent')) != (self.max_number_shafts - 2):
    #                       valid = False
    #           if len(node) == len(list_edges) and valid:
    #               for i_nd, nd in enumerate(node): 
    #                   dict_connections[edges[i_nd]] = self.connections[nd]
    #                   self.gearbox.gearbox_connections[edges[i_nd]] = self.connections[nd]
    #               # gearbox = self.gearbox.copy()
    #               # gearbox.gearbox_connections = self.gearbox.gearbox_connections
    #               list_dict_connections.append(copy.copy(dict_connections))
    #               # list_gearbox.append(gearbox)
    #           tree.NextNode(valid)
        
    #     return list_dict_connections
      
              
    # def solutions(self):
        
    #     list_gearbox_connections = self.connections_decision_tree()
    #     # gearbox_possible_solutions = []
    #     list_multi_entry_gearbox_graphs = []
    #     list_multi_entry_paths = []
    #     list_multi_entry_paths_edges = []
    #     list_multi_entry_counter_paths_between_2shafts = []
    #     # list_list_counter_paths_between_2shafts = []
        
    #     for gearbox_connections in list_gearbox_connections:
    #         list_gearbox_graphs = []
    #         list_paths = []
    #         list_paths_edges = []
    #         list_counter_paths_between_2shafts = []
    #         gearbox_graph = nx.Graph()
    #         for gearbox_connection in gearbox_connections:
    #             if gearbox_connections[gearbox_connection] != 'inexistent':
    #                 gearbox_graph.add_edges_from([(gearbox_connection[0], gearbox_connection[1], {'connection':gearbox_connections[gearbox_connection]})])
    #             # else:
    #             #     gearbox_graph.add_nodes_from([gearbox_connection[0], gearbox_connection[1]])
            
            
    #         for n in range(self.number_inputs):
    #             paths = []
    #             if 'S' + str(n+1) in gearbox_graph and 'S'+str(self.max_number_shafts) in gearbox_graph:
    #                 count = 0
    #                 for path in nx.all_simple_paths(gearbox_graph, source = 'S' + str(n+1), target = 'S'+str(self.max_number_shafts)):
    #                     count += 1
    #                     paths.append(path)
    #                 paths_edges = []
    #                 for path in map(nx.utils.pairwise, paths):
    #                     paths_edges.append(list(path))
    
                    
    #                 if count == len(self.gearbox.speed_ranges):
    #                     valid = True
    #                     for k in range(self.number_inputs):
    #                         if k != n:
    #                             if 'S'+str(k+1) in [path_node for path in paths for path_node in path]:
    #                                 valid = False
                        
    #                     # for node in gearbox_graph.nodes(): 
    #                     #     if node not in [path_node for path in paths for path_node in path]:
    #                     #         valid = False 
                                
    #                     # if len(list_paths) != 0:
    #                     #     for j, paths_list in enumerate(list_paths_edges):
    #                     #         counter = 0
    #                     #         for path in paths_edges: 
    #                     #             if path in paths_list:
    #                     #                 counter +=1
    #                     #         if counter == count:
    #                     #             valid = False 
    #                     graph_paths_nodes = [node for path in paths for node in path]
    #                     counter_paths_between_2shafts = {}
    #                     for i in range(self.max_number_shafts):
    #                         for j in range(self.max_number_shafts):
    #                             if i < j and j != n:
    #                                 if 'S'+str(i+1) in graph_paths_nodes and 'S'+str(j+1) in graph_paths_nodes:
    #                                     counter_paths_between_2shafts['S'+str(i+1)+'-S'+str(j+1)] = (len(list(nx.all_simple_paths(gearbox_graph, 'S'+str(i+1), 'S'+str(j+1)))),\
    #                                                                                                   dict(Counter([len(path) for path  in nx.all_simple_paths(gearbox_graph, 'S'+str(i+1), 'S'+str(j+1))])))
    #                                     # print(len(list(nx.all_simple_paths(gearbox_graph, 'S'+str(i+1), 'S'+str(j+1)))), dict(Counter([len(path) for path  in nx.all_simple_paths(gearbox_graph, 'S'+str(i+1), 'S'+str(j+1))])))
    #                     if list(counter_paths_between_2shafts.values()) in [list(counter.values()) for counter in list_multi_entry_counter_paths_between_2shafts]:
    #                         # print('yes')
    #                         valid = False
                                        
                
    #                     if valid:
    #                         list_paths.append(paths)
    #                         list_gearbox_graphs.append(gearbox_graph)
    #                         list_paths_edges.append(paths_edges)
    #                         list_counter_paths_between_2shafts.append(counter_paths_between_2shafts)
    #         # print('here it is, see if it is empty: ',[list(counter.values()) for list_counter in list_multi_entry_counter_paths_between_2shafts for counter in list_counter])
    #         if len(list_paths) == self.number_inputs:
    #             list_multi_entry_gearbox_graphs.append(gearbox_graph)
    #             list_multi_entry_paths.append(list_paths)
    #             list_multi_entry_paths_edges.append(list_paths_edges)
    #             list_multi_entry_counter_paths_between_2shafts.extend(list_counter_paths_between_2shafts)
                   
    #     return list_multi_entry_gearbox_graphs, list_multi_entry_paths, list_multi_entry_paths_edges, list_multi_entry_counter_paths_between_2shafts
            
    
# def solutions(self):
    
#     list_gearbox_connections = self.connections_decision_tree()
#     # gearbox_possible_solutions = []
#     list_gearbox_graphs = []
#     list_paths = []
#     list_paths_edges = []
#     list_counter_paths_between_2shafts = []
#     # list_list_counter_paths_between_2shafts = []
    
#     for gearbox_connections in list_gearbox_connections:
#         gearbox_graph = nx.Graph()
#         for gearbox_connection in gearbox_connections:
#             if gearbox_connections[gearbox_connection] != 'inexistent':
#                 gearbox_graph.add_edges_from([(gearbox_connection[0], gearbox_connection[1], {'connection':gearbox_connections[gearbox_connection]})])
#             # else:
#             #     gearbox_graph.add_nodes_from([gearbox_connection[0], gearbox_connection[1]])
#         count = 0
#         paths = []
#         if 'S1' in gearbox_graph and 'S'+str(self.max_number_shafts) in gearbox_graph:
#             for path in nx.all_simple_paths(gearbox_graph, source = 'S1', target = 'S'+str(self.max_number_shafts)):
#                 count += 1
#                 paths.append(path)
#             paths_edges = []
#             for path in map(nx.utils.pairwise, paths):
#                 paths_edges.append(list(path))

            
#             if count == len(self.gearbox.speed_ranges):
#                 valid = True
#                 for node in gearbox_graph.nodes():
#                     if node not in [path_node for path in paths for path_node in path]:
#                         valid = False 
                        
#                 # if len(list_paths) != 0:
#                 #     for j, paths_list in enumerate(list_paths_edges):
#                 #         counter = 0
#                 #         for path in paths_edges: 
#                 #             if path in paths_list:
#                 #                 counter +=1
#                 #         if counter == count:
#                 #             valid = False 
#                 graph_paths_nodes = [node for path in paths for node in path]
#                 counter_paths_between_2shafts = {}
#                 for i in range(self.max_number_shafts):
#                     for j in range(self.max_number_shafts):
#                         if i < j:
#                             if 'S'+str(i+1) in graph_paths_nodes and 'S'+str(j+1) in graph_paths_nodes:
#                                 counter_paths_between_2shafts['S'+str(i+1)+'-S'+str(j+1)] = (len(list(nx.all_simple_paths(gearbox_graph, 'S'+str(i+1), 'S'+str(j+1)))),\
#                                                                                              dict(Counter([len(path) for path  in nx.all_simple_paths(gearbox_graph, 'S'+str(i+1), 'S'+str(j+1))])))
#                                 # print(len(list(nx.all_simple_paths(gearbox_graph, 'S'+str(i+1), 'S'+str(j+1)))))
#                 if list(counter_paths_between_2shafts.values()) in [list(counter.values()) for counter in list_counter_paths_between_2shafts]:
#                     valid = False
                                
        
#                 if valid:
#                     list_paths.append(paths)
#                     list_gearbox_graphs.append(gearbox_graph)
#                     list_paths_edges.append(paths_edges)
#                     list_counter_paths_between_2shafts.append(counter_paths_between_2shafts)
               
#     return list_gearbox_graphs, list_paths, list_paths_edges, list_counter_paths_between_2shafts
              
    
    
        
        
        
        
        # if node[-self.max_number_shafts:].count(self.connections.index('inexistent')) != (self.max_number_shafts - 2) or node[-self.max_number_shafts:].count(self.connections.index('inexistent')) != (self.max_number_shafts - 3):
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
#         list_node = []
#         list_gear = []
#         # gearbox = self.gearbox
        
        
       
        
#         for i in range(self.max_number_meshes): 
#             list_node.append(self.min_max_number_shafts_per_mesh[1] - self.min_max_number_shafts_per_mesh[0])
#             list_node.append(self.number_connections)
#             list_gear.append(i + 1)
        
        
#         tree = dt.RegularDecisionTree(list_node)
#         list_gearbox = []
#         list_valid_nodes = []
#         # shafts = []
        
#         while not tree.finished:
#               valid = True
#               node = tree.current_node
#               # connections = []
#               if len(node)%2 == 0: 
#                   number_shaft = node[-1] 
              
#               # if len(node)%2 != 0:
#               #     shaft = self.list_shafts[node[-1]]
#               # else: 
#               #     connections.append(node[-1])

#               # gearbox.gear_connections[len(node) - 1] = node[-1]
             
#               if len(node) <= len(list_gear)/2 + 1:
#                   if node[-1] != 0:
#                       valid  = False
#               else:
#                   if node[-1] == 2:
#                       valid = False
             
#               if len(node)==len(list_gear) and valid:
#                   list_connections 
#                   list_gearbox.append(copy.deepcopy(gearbox))
#                   list_valid_nodes.append(node)
                 
#               tree.NextNode(valid)
             
#         return list_gearbox, list_valid_nodes
             
        
        
# # avant j'utilisais les meshes et les arbres pour le noueds, mais je voyais pas commet faire le contrôle après pour le deuxième point que tu avait proposé vendredi, de vérifier si un engrènement n'est connecté que 


        
    
   # while not tree.finished:
   #            valid = True
   #            node = tree.current_node
   #            dict_connections[edges[len(node)-1]] = self.connections[node[-1]]
   #            # print(dict_connections)
   #            # for dict_connection in dict_connections:
   #            if len(node)%self.max_number_shafts == 0:
   #            #     print(len(node))
   #            #     print('passa por aqui sim')
   #            #     break
   #            # if len(node)%self.max_number_shafts == 0:
   #            #     # print(len(node))
   #            #     print('passa por aqui sim')
   #            #     count+=1
   #            #     print('length node: ', len(node))
   #            #     if count == 10:
   #            #         break
   #                 # print('length node: ', len(node))
   #                 if node[-self.max_number_shafts:].count(self.connections.index('inexistent')) < self.max_number_shafts:
   #                     if node[-self.max_number_shafts:].count(self.connections.index('inexistent')) != (self.max_number_shafts - 2):
   #                         valid = False
   #            #         # else:
   #            #         #     if node[-self.max_number_shafts:].count(self.connections.index('free')) != 2 or node[-self.max_number_shafts:].count(self.connections.index('fixed')) != 2:
   #            #         #         valid = False

   #            if len(node) == len(list_edges) and valid:
                   
   #                # placer=0
   #                for i_nd, nd in enumerate(node):
                       
   #                #     if (i_nd+1)%self.max_number_shafts == 0:
   #                #         # if node[placer:i_nd+1].count(self.connections.index('inexistent')) < self.max_number_shafts:
                              
   #                #           if node[placer:i_nd+1].count(self.connections.index('inexistent')) != self.max_number_shafts-2:
   #                #               valid = False
   #                #           placer += self.max_number_shafts
   #                # if valid:
   #                #     list_gearbox.append(gearbox)
   #                #     list_nodes.append(node)
                              
                           
                           
   #                     gearbox.gearbox_connections[edges[i_nd]] = self.connections[nd]
   #                list_gearbox.append(gearbox)
   #                list_nodes.append(node)
   #            # print("nexxtnode")
   #            tree.NextNode(valid)
        
   #      return list_gearbox, list_nodes 
    
    
    
    
    # def connections_decision_tree(self):
    #     list_node = []
    #     list_edges = []
    #     # gearbox = self.gearbox.copy()
    #     gearbox_graph = self.gearbox_graph()
    #     dict_connections = {}
    #     list_dict_connections = []
    #     for edge in gearbox_graph.edges():
    #         list_node.append(len(self.connections))
    #         list_edges.append(edge)
    #     edges = []
    #     for gear in range(self.max_number_gears):
    #         for shaft in range(self.max_number_shafts):
    #             if ('G' + str(gear+1), 'S' + str(shaft+1)) in list_edges:
    #                 edges.append(('G' + str(gear+1), 'S' + str(shaft+1)))
    #                 dict_connections[('G' + str(gear+1), 'S' + str(shaft+1))] = 0
    #             if ('S' + str(shaft+1), 'G' + str(gear+1)) in list_edges:
    #                 edges.append(('S' + str(shaft+1), 'G' + str(gear+1)))
    #                 dict_connections[('S' + str(shaft+1), 'G' + str(gear+1))] = 0
    #     print(edges)
        
        
    #     # tree = dt.RegularDecisionTree(list_node)
    #     # list_gearbox = []
    #     # list_nodes = []
    #     # while not tree.finished:
    #     #       valid = True
    #     #       node = tree.current_node
    #     #       if len
    #     #       if len(node)%self.max_number_shafts == 0:
    #     #           if node[-self.max_number_shafts:].count(self.connections.index('inexistent')) < self.max_number_shafts:
    #     #               if node[-self.max_number_shafts:].count(self.connections.index('inexistent')) != (self.max_number_shafts - 2):
    #     #                   valid = False
    #     #       if len(node) == len(list_edges) and valid:
    #     #           for i_nd, nd in enumerate(node): 
    #     #               dict_connections[edges[i_nd]] = self.connections[nd]
    #     #               self.gearbox.gearbox_connections[edges[i_nd]] = self.connections[nd]
    #     #           # gearbox = self.gearbox.copy()
    #     #           # gearbox.gearbox_connections = self.gearbox.gearbox_connections
    #     #           list_dict_connections.append(copy.copy(dict_connections))
    #     #           # list_gearbox.append(gearbox)
    #     #       tree.NextNode(valid)
        
    #     # return list_dict_connections
    
    
    