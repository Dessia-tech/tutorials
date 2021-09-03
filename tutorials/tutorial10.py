# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 13:30:58 2021

@author: wirajan
"""

from dessia_common import DessiaObject, DisplayObject
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
from itertools import product
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from sklearn.manifold import MDS


class EfficiencyMap(DessiaObject):
    """
    Build the engine map and then determine its efficiency
    """
    _standalone_in_db = True
    def __init__(self, engine_speeds: List[float], engine_torques: List[float],
                 mass_flow_rate: List[List[float]], fuel_hv: float, name: str = ''):
        self.engine_speeds = engine_speeds  # in rad/s
        self.engine_torques = engine_torques  # in Nm
        self.mass_flow_rate = mass_flow_rate
        self.fuel_hv = fuel_hv  # fuel lower heating value in J/kg

        DessiaObject.__init__(self,name=name)

        BSFC = []
        for i, engine_speed in enumerate(self.engine_speeds):
            list_bsfc = []
            for j, engine_torque in enumerate(self.engine_torques):
                bsfc = self.mass_flow_rate[i][j]/(engine_speed*engine_torque)  # in kg/J
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
    def __init__(self, cycle_speeds: List[float], car_mass: float,
                 tire_radius: float, dt: float = 1, name: str = ''):
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
            torque = acceleration*car_mass*tire_radius/2  #torque in Nm
            cycle_torques.append(torque)
            
        self.cycle_torques = cycle_torques 


class Engine(DessiaObject):
    _standalone_in_db = True

    def __init__(self, efficiency_map : EfficiencyMap, setpoint_speed: float,
                 setpoint_torque: float, name: str = ''):
        self.efficiency_map = efficiency_map
        self.setpoint_speed = setpoint_speed
        self.setpoint_torque = setpoint_torque

        DessiaObject.__init__(self,name=name)
    
    def efficiency(self, speed:float, torque:float):
        interpolate = interp2d(self.efficiency_map.engine_torques,
                               self.efficiency_map.engine_speeds,
                               self.efficiency_map.efficiencies)
        interpolate_efficiency = interpolate(torque, speed)
        return interpolate_efficiency[0]
    
    def consumption_efficiency(self, speed:float, torque: float):
        interpolate = interp2d(self.efficiency_map.engine_torques,
                               self.efficiency_map.engine_speeds,
                               self.efficiency_map.bsfc)
        interpolate_consumption_efficiency = interpolate(torque, speed)
        return float(interpolate_consumption_efficiency[0])


class GearBox(DessiaObject):
    _standalone_in_db = True
    _non_serializable_attributes = ['graph']

    def __init__(self, engine: Engine, speed_ranges: List[List[float]],
                 ratios: List[float] = None,
                 name: str = ''):
        self.engine = engine
        self.speed_ranges = speed_ranges
        self.ratios = ratios
        DessiaObject.__init__(self, name=name)
        self.graph = None
        self.average_path_length = None
        self.average_clutch_distance = None
        self.number_shafts = None
        self.number_gears = None
        self.std_clutch_distance = None
        self.std_gears_distance = None
        self.density = None
        self.ave_l_ns = None

    def update_gb_graph(self, graph):
        self.graph = graph
        self.ave_l_ns = graph.graph['Average length path/N shafts']
        self.average_path_length = graph.graph['Average length path']
        self.average_clutch_distance = graph.graph['Average distance clutch-input']
        self.number_shafts = graph.graph['Number of shafts']
        self.number_gears = graph.graph['Number of gears']
        self.std_clutch_distance = graph.graph['Standard deviation distante input/cluches']
        self.density = graph.graph['Density']

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
        if cycle_speed == 0:
            engine_speed = self.engine.setpoint_speed
            engine_torque = self.engine.setpoint_torque
            fuel_consumption_gpkwh = self.engine.consumption_efficiency(
                engine_speed, engine_torque
            )
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

        return [gear, ratio, fuel_consumption_gpkwh,
                engine_speed, engine_torque]

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

    def to_dict(self, subobjects_id={}):
        """
        Export dictionary
        """
        d = {}
        d['engine'] = self.engine.to_dict()
        d['speed_ranges'] = self.speed_ranges
        d['ratios'] = self.ratios
        d['average_path_length'] = self.average_path_length
        d['average_clutch_distance'] = self.average_clutch_distance
        d['number_gears'] = self.number_gears
        d['number_shafts'] = self.number_shafts
        d['Standard deviation distante input/cluches'] = self.std_clutch_distance
        d['Standard deviation distante input/gears'] = self.std_gears_distance
        d['Density'] = self.density
        d['graph'] = nx.readwrite.json_graph.node_link_data(self.graph)
        d['name'] = self.name
        d['ave_l_ns'] = self.ave_l_ns
        d['object_class'] = 'tutorials.tutorial10.GearBox'

        return d

    @classmethod
    def dict_to_object(cls, d):
        obj = cls(engine=Engine.dict_to_object(d['engine']),
                  speed_ranges=d['speed_ranges'],
                  ratios=d['ratios'], name=d['name'])
        obj.graph = nx.readwrite.json_graph.node_link_graph(d['graph'])
        obj.average_clutch_distance = d['average_clutch_distance']
        obj.average_path_length = d['average_path_length']
        obj.number_gears = d['number_gears']
        obj.number_shafts = d['number_shafts']
        obj.std_clutch_distance = d['Standard deviation distante input/cluches']
        obj.std_gears_distance = d['Standard deviation distante input/gears']
        obj.density = d['Density']
        obj.ave_l_ns = d['ave_l_ns']
        return obj


class GearBoxResults(DessiaObject): 
    _standalone_in_db = True

    def __init__(self, gearbox: GearBox, wltp_cycle: WLTPCycle,
                 engine_speeds: List[float],
                 engine_torques: List[float], 
                 fuel_consumptions: List[float],
                 gears: List[float], ratios: List[float],
                 average_fuel_consumption: float,
                 name: str = ''):
        self.gearbox = gearbox
        self.wltp_cycle = wltp_cycle
        self.engine_speeds = engine_speeds
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
        point_style = plot_data.PointStyle(color_fill=color_fill,
                                           color_stroke=color_stroke)
        axis = plot_data.Axis()

        attributes = ['c_s', 'f_cons (g/kWh)']
        tooltip = plot_data.Tooltip(attributes=attributes,)
        objects = [plot_data.Scatter(tooltip=tooltip, x_variable=attributes[0],
                                     y_variable=attributes[1],
                                     point_style=point_style,
                                     elements=points, axis=axis)]

        attributes = ['whl_t', 'f_cons (g/kWh)']
        tooltip = plot_data.Tooltip(attributes=attributes)
        objects.append(plot_data.Scatter(tooltip=tooltip,
                                         x_variable=attributes[0],
                                         y_variable=attributes[1],
                                         point_style=point_style,
                                         elements=points, axis=axis))

        attributes = ['w_e','t_e','f_cons (g/kWh)']
        edge_style = plot_data.EdgeStyle()
        rgbs = [[192, 11, 11], [14, 192, 11], [11, 11, 192]]
        objects.append(plot_data.ParallelPlot(elements=points,
                                              edge_style=edge_style,
                                              disposition='vertical',
                                              axes=attributes,
                                              rgbs=rgbs))

        coords = [(0, 0), (500, 0), (1000, 0)]
        sizes = [plot_data.Window(width=500, height=500),
                 plot_data.Window(width=500, height=500),
                 plot_data.Window(width=500, height=500)]
        multiplot = plot_data.MultiplePlots(elements=points, plots=objects,
                                            sizes=sizes, coords=coords)
        
        list_colors = [BLUE, BROWN, GREEN, BLACK]
        graphs2d = []
        point_style = plot_data.PointStyle(color_fill=RED, color_stroke=BLACK,
                                           size=1)

        tooltip = plot_data.Tooltip(attributes=['sec', 'gear'])
        edge_style = plot_data.EdgeStyle(line_width=0.5,
                                         color_stroke=list_colors[0])
        elements = []
        for i, gear in enumerate(self.gears):
            elements.append({'sec': cycle_time[i], 'gear': gear})         
        dataset = plot_data.Dataset(elements=elements,
                                    edge_style=edge_style,
                                    tooltip=tooltip,
                                    point_style=point_style)
        graphs2d.append(plot_data.Graph2D(graphs=[dataset],
                                          x_variable='sec',
                                          y_variable='gear'))

        tooltip = plot_data.Tooltip(attributes=['sec', 'f_cons (g/kWh)'])
        edge_style = plot_data.EdgeStyle(line_width=0.5,
                                         color_stroke=list_colors[0])
        elements = []
        for i, gear in enumerate(self.gears):
            point = {'sec': cycle_time[i],
                     'f_cons (g/kWh)': self.fuel_consumptions[i]*3.6e9}
            elements.append(point)
        dataset = plot_data.Dataset(elements=elements,
                                    edge_style=edge_style,
                                    tooltip=tooltip,
                                    point_style=point_style)
        graphs2d.append(plot_data.Graph2D(graphs=[dataset],
                                          x_variable='sec',
                                          y_variable='f_cons (g/kWh)'))

        tooltip = plot_data.Tooltip(attributes=['sec', 'w_e'])
        edge_style = plot_data.EdgeStyle(line_width=0.5,
                                         color_stroke=list_colors[2])
        elements = []
        for i, torque in enumerate(self.wltp_cycle.cycle_torques):
            point = {'sec': cycle_time[i], 'w_e': self.engine_speeds[i]}
            elements.append(point)
        dataset = plot_data.Dataset(elements=elements,
                                    edge_style=edge_style,
                                    tooltip=tooltip,
                                    point_style=point_style)
        graphs2d.append(plot_data.Graph2D(graphs=[dataset],
                                          x_variable='sec',
                                          y_variable='w_e'))

        tooltip = plot_data.Tooltip(attributes=['sec', 'w_t'])
        edge_style = plot_data.EdgeStyle(line_width=0.5,
                                         color_stroke=list_colors[3])
        elements = []
        for i, torque in enumerate(self.wltp_cycle.cycle_torques):
            point = {'sec': cycle_time[i], 'w_t': self.engine_torques[i]}
            elements.append(point)
        dataset = plot_data.Dataset(elements=elements,
                                    edge_style=edge_style,
                                    tooltip=tooltip,
                                    point_style=point_style)
        graphs2d.append(plot_data.Graph2D(graphs=[dataset],
                                          x_variable='sec',
                                          y_variable='w_t'))

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
    
    def __init__(self, gearbox: GearBox, wltp_cycle: WLTPCycle,
                 first_gear_ratio_min_max: Tuple[float, float],
                 coeff_between_gears: List[Tuple[float, float]] = None, 
                 name: str = ''):
        self.gearbox = gearbox
        self.wltp_cycle = wltp_cycle
        self.coeff_between_gears = coeff_between_gears
        self.first_gear_ratio_min_max = first_gear_ratio_min_max
        DessiaObject.__init__(self, name=name)
        
        if self.coeff_between_gears is None:
            self.coeff_between_gears = (len(self.gearbox.speed_ranges)-1)*[[0.5,1]]
 
        bounds=[]
        for i in range(len(self.gearbox.speed_ranges)):
            if i == 0:
                bounds.append([self.first_gear_ratio_min_max[0],
                               self.first_gear_ratio_min_max[1]])
            else: 
                bounds.append([self.coeff_between_gears[i-1][0],
                               self.coeff_between_gears[i-1][1]])
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
                gearbox_results = GearBoxResults(gearbox,
                                                 self.wltp_cycle,
                                                 self.engine_speeds,
                                                 self.engine_torques,
                                                 self.fuel_consumptions,
                                                 self.gears, 
                                                 self.ratios,
                                                 self.average_fuel_consumption) 
                list_gearbox_results.append(gearbox_results)
                
        return list_gearbox_results
    
    
class GearBoxGenerator(DessiaObject):
    _standalone_in_db = True

    def __init__(self, gearbox: GearBox, number_inputs: int,
                 max_number_shaft_assemblies: int,
                 max_number_gears: int, name: str = ''):
        self.gearbox = gearbox
        self.number_inputs = number_inputs
        self.max_number_shaft_assemblies = max_number_shaft_assemblies
        self.max_number_gears = max_number_gears
        DessiaObject.__init__(self, name=name)

    def generate_connections(self):
        list_node = []
        connections = []
        list_dict_connections = []

        for i in range(self.max_number_shaft_assemblies):
            for j in range(self.max_number_shaft_assemblies):
                if i < j:
                    connections.append((i + 1, j + 1))
        connections.append(None)
        for gear in range(self.max_number_gears):
            list_node.append(len(connections))
        tree = dt.RegularDecisionTree(list_node)
        while not tree.finished:
            valid = True
            node = tree.current_node
            new_node = []
            for nd in node:
                if nd != len(connections) - 1:
                    new_node.append(nd)
            if len(new_node) > 1:
                if connections[new_node[-1]][0] != connections[new_node[-2]][0]:
                    if connections[new_node[-1]][0] != \
                            connections[new_node[-2]][1]:
                        valid = False
            if len(new_node) == 0:
                valid = False
            if len(node) == self.max_number_gears and valid:
                dict_connections = {}
                for i_node, nd in enumerate(new_node):
                    dict_connections['G' + str(i_node + 1)] = connections[nd]
                list_dict_connections.append(dict_connections)
            tree.NextNode(valid)
        return list_dict_connections

    def generate_paths(self, list_gearbox_connections):
        # list_gearbox_connections = self.generate_connections()
        list_gearbox_graphs = []
        list_paths = []
        list_paths_edges = []
        list_dict_connections = []
        for gearbox_connections in list_gearbox_connections:
            gearbox_graph = nx.Graph()
            for gearbox_connection in gearbox_connections:
                gearbox_graph.add_edge(
                    'S' + str(gearbox_connections[gearbox_connection][0]),
                    gearbox_connection)
                gearbox_graph.add_edge(gearbox_connection, 'S' + str(
                    gearbox_connections[gearbox_connection][1]))

            number_shafts = 0
            number_gears = 0
            input_shaft = 'S' + str(min([shaft for gearbox_connection in \
                                         gearbox_connections.values() for shaft
                                         in gearbox_connection]))
            output_shaft = 'S' + str(max([shaft for gearbox_connection in \
                                          gearbox_connections.values() for
                                          shaft in gearbox_connection]))
            for node in gearbox_graph.nodes():
                if node == input_shaft:
                    gearbox_graph.nodes()[node]['Node Type'] = 'Input Shaft'
                    number_shafts += 1
                elif node == output_shaft:
                    gearbox_graph.nodes()[node]['Node Type'] = 'Output Shaft'
                    number_shafts += 1
                elif 'S' in node:
                    gearbox_graph.nodes()[node]['Node Type'] = 'Shaft'
                    number_shafts += 1
                else:
                    gearbox_graph.nodes()[node]['Node Type'] = 'Gear'
                    number_gears += 1
            paths = []
            count = 0
            average_lengths = []
            for path in nx.all_simple_paths(gearbox_graph, input_shaft,
                                            output_shaft):
                paths.append(path)
                average_lengths.append(len(path))
                count += 1
            paths_edges = []
            for path in map(nx.utils.pairwise, paths):
                paths_edges.append(list(path))

            if count == len(self.gearbox.speed_ranges):
                valid = True
                gears_path_lengths = []
                for node in gearbox_graph.nodes():
                    if node not in [path_node for path in paths for path_node
                                    in path]:
                        valid = False
                    if gearbox_graph.nodes()[node]['Node Type'] == 'Gear':
                        gears_path_lengths.append(
                            nx.shortest_path_length(gearbox_graph, input_shaft,
                                                    node))
                for graph in list_gearbox_graphs:
                    node_match = iso.categorical_node_match('Node Type',
                                                            'Shaft')
                    if nx.is_isomorphic(gearbox_graph, graph,
                                        node_match=node_match):
                        valid = False
                if valid:
                    gearbox_graph.graph['Average length path/N shafts'] = mean(
                        average_lengths) / number_shafts
                    gearbox_graph.graph['Average length path'] = mean(
                        average_lengths)
                    gearbox_graph.graph['Number of shafts'] = number_shafts
                    gearbox_graph.graph['Number of gears'] = number_gears
                    # gearbox_graph.graph['Standard deviation distante input/gears'] = np.std(gears_path_lengths)
                    gearbox_graph.graph['Density'] = nx.density(gearbox_graph)
                    list_gearbox_graphs.append(gearbox_graph)
                    list_paths.append(paths)
                    list_paths_edges.append(paths_edges)
                    list_dict_connections.append(gearbox_connections)

        return list_gearbox_graphs  # , list_paths, list_paths_edges, list_counter_paths_between_2shafts,list_dict_connections

    def clutch_analisys(self, list_path_generated_graphs):
        new_list_gearbox_graphs = []
        list_clutch_combinations = []
        list_cycles = []
        list_dict_clutch_connections = []
        for graph in list_path_generated_graphs:
            for node in graph.nodes():
                if graph.nodes()[node]:
                    if graph.nodes()[node]['Node Type'] == 'Input Shaft':
                        input_shaft = node
            cycles = nx.cycle_basis(graph, root=input_shaft)
            list_cycles.append(cycles)
            list_cycle_shafts = []
            for cycle in cycles:
                cycle_shafts = []
                for node in cycle:
                    if 'S' in node:
                        cycle_shafts.append(node)
                list_cycle_shafts.append(cycle_shafts)
            clutch_combinations = list(product(*list_cycle_shafts))
            list_clutch_combinations.append(clutch_combinations)
            for clutch_combination in clutch_combinations:
                graph_copy = copy.deepcopy(graph)
                dict_clutch_connections = {}
                for i_cycle, cycle in enumerate(cycles):
                    for i_node, node in enumerate(cycle):
                        if clutch_combination[i_cycle] == node:
                            if clutch_combination[i_cycle] == cycle[-1]:
                                dict_clutch_connections[i_cycle + 1] = (
                                cycle[0], cycle[i_node - 1])
                                graph_copy.nodes()[node]['Clutch'] = True
                                graph_copy.add_edges_from(
                                    [(cycle[0], node, {'Clutch': True}), (
                                    cycle[i_node - 1], node,
                                    {'Clutch': True})])
                            else:
                                dict_clutch_connections[i_cycle + 1] = (
                                cycle[i_node + 1], cycle[i_node - 1])
                                graph_copy.nodes()[node]['Clutch'] = True
                                graph_copy.add_edges_from([(cycle[i_node + 1],
                                                            node,
                                                            {'Clutch': True}),
                                                           (cycle[i_node - 1],
                                                            node,
                                                            {'Clutch': True})])
                clutch_path_lengths = []
                for node in graph_copy.nodes():
                    if 'Clutch' in list(graph_copy.nodes()[node].keys()):
                        clutch_path_lengths.append(
                            nx.shortest_path_length(graph_copy, input_shaft,
                                                    node))
                graph_copy.graph['Average distance clutch-input'] = mean(
                    clutch_path_lengths)
                graph_copy.graph[
                    'Standard deviation distante input/cluches'] = np.std(
                    clutch_path_lengths)
                list_dict_clutch_connections.append(dict_clutch_connections)
                new_list_gearbox_graphs.append(graph_copy)

        return new_list_gearbox_graphs, list_dict_clutch_connections, list_clutch_combinations, list_cycles

    def generate(self):
        generate_connections = self.generate_connections()
        generate_paths = self.generate_paths(generate_connections)
        clutch_analisys = self.clutch_analisys(generate_paths)
        list_gearbox_solutions = []
        clutch_gearbox_graphs = clutch_analisys[0]
        list_clutch_connections = clutch_analisys[1]
        list_clutch_combinations = [clutch_combination for clutch_combinations
                                    in clutch_analisys[2] for
                                    clutch_combination in clutch_combinations]
        list_clutch_gearbox_graphs = []
        for i_graph, graph in enumerate(clutch_gearbox_graphs):
            valid = True
            graph_copy = copy.deepcopy(graph)
            clutch_connections = list_clutch_connections[i_graph]
            for i, connections in enumerate(
                    list(list_clutch_connections[i_graph])):
                if i != 0:
                    if list_clutch_connections[i_graph][i + 1] == \
                            list_clutch_connections[i_graph][i]:
                        print(list_clutch_connections[i_graph][i + 1],
                              list_clutch_connections[i_graph][i])
                        valid = False
                        break
            if not valid:
                continue
            for node in graph.nodes():
                if 'Clutch' in list(graph.nodes()[node].keys()):
                    for edge in graph.edges():
                        if node in edge:
                            clutch_link_values = [value for values in
                                                  clutch_connections.values()
                                                  for value in values]
                            if edge[0] in clutch_link_values or edge[
                                1] in clutch_link_values:
                                graph_copy.remove_edge(edge[0], edge[1])
                                if 'S' in edge[0]:
                                    graph_copy.add_edge(edge[1],
                                                        edge[0] + '-' + edge[
                                                            1])
                                    graph_copy.add_edge(edge[0],
                                                        edge[0] + '-' + edge[
                                                            1])
                                else:
                                    graph_copy.add_edge(edge[0],
                                                        edge[1] + '-' + edge[
                                                            0])
                                    graph_copy.add_edge(edge[1],
                                                        edge[1] + '-' + edge[
                                                            0])
            for node in graph_copy.nodes():
                if graph_copy.nodes()[node]:
                    if graph_copy.nodes()[node]['Node Type'] == 'Input Shaft':
                        input_shaft = node
                    if graph_copy.nodes()[node]['Node Type'] == 'Output Shaft':
                        output_shaft = node
            paths = nx.all_simple_paths(graph_copy, input_shaft, output_shaft)

            for path in paths:
                if not any(('S' in node and 'G' in node) for node in path):
                    valid = False

            for i_shaft, shaft in enumerate(list_clutch_combinations[i_graph]):
                graph_copy.add_edges_from(
                    [(shaft + '-' + clutch_connections[i_shaft + 1][0],
                      shaft + '-' + clutch_connections[i_shaft + 1][1],
                      {'Clucth': True})])
            if valid:
                gearbox = self.gearbox.copy()
                gearbox.update_gb_graph(graph_copy)
                list_gearbox_solutions.append(gearbox)
                list_clutch_gearbox_graphs.append(graph_copy)

        return list_gearbox_solutions  # , list_clutch_gearbox_graphs

    def draw_graph(self, graphs_list: List[nx.Graph],
                   max_number_graphs: int = None):

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
            edges_clutch = []
            for edge in graph.edges():
                if graph.edges()[edge]:
                    edges_clutch.append(edge)
                else:
                    edges.append(edge)

            pos = nx.kamada_kawai_layout(graph)

            nx.draw_networkx_nodes(graph, pos, shafts, node_color='skyblue',
                                   node_size=1000)
            nx.draw_networkx_nodes(graph, pos, S_G, node_color='grey',
                                   node_size=500)
            nx.draw_networkx_nodes(graph, pos, gears, node_shape='s',
                                   node_color='steelblue', node_size=1000)
            nx.draw_networkx_edges(graph, pos, edges_clutch, edge_color='red',
                                   width=3)
            nx.draw_networkx_edges(graph, pos, edges)
            labels = {element: element for element in shafts + S_G + gears}
            nx.draw_networkx_labels(graph, pos, labels=labels)
            if max_number_graphs is not None:
                if i >= max_number_graphs:
                    break


class Clustering(DessiaObject):
    standalone_in_db = True

    def __init__(self, gearboxes: List[GearBox], name: str = ""):
        self.gearboxes = gearboxes
        DessiaObject.__init__(self, name=name)
        dict_features = {}
        for gearbox in self.gearboxes:
            for attr in gearbox.graph.graph.keys():
                if attr in dict_features.keys():
                    variable = dict_features[attr]
                    variable.append(gearbox.graph.graph[attr])
                    dict_features[attr] = variable
                else:
                    dict_features[attr] = [gearbox.graph.graph[attr]]
        self.dict_features = dict_features
        self.df = pd.DataFrame.from_dict(self.dict_features)
        df_scaled = self.normalize(self.df)
        self.labels, self.n_clusters = self.dbscan(df_scaled)
        family_groups = self.family_groups(df_scaled, self.labels)
        self.clusters = family_groups[0]
        self.labels_reordered = family_groups[1]
        self.list_indexes_groups = family_groups[2]
        self.gearboxes_ordered = family_groups[3]
        self.matrix_mds = family_groups[4]
 
    def normalize(self, df):
        
        scaler = MinMaxScaler()
        scaler.fit(df)
        df_scaled = scaler.fit_transform(df)
        return df_scaled
 
    def dbscan(self, df):
        db = DBSCAN(eps=0.7, min_samples=3)
        db.fit(df)
        labels = [int(label) for label in list(db.labels_)]
        # Number of clusters in labels, ignoring noise if present.
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        print('Estimated number of clusters:', n_clusters)
        return labels, n_clusters
    
    def family_groups(self, df, labels):
        encoding_mds = MDS()
        matrix_mds = [element.tolist() for element in encoding_mds.fit_transform(df)]
        clusters = []
        list_indexes_groups =[]
        gearboxes_indexes = []
        index = 0
        cluster_labels_reordered = []
        for label in labels:
            if label not in clusters:
                clusters.append(label)
        for j, cluster in enumerate(clusters):
            indexes = []
            for i, label in enumerate(labels):
                if cluster == label:
                    cluster_labels_reordered.append(label)
                    indexes.append(index)
                    index += 1
                    gearboxes_indexes.append(i)
            list_indexes_groups.append(indexes)
        new_gearboxes_order =[]
        new_matrix_mds = []
        for index in gearboxes_indexes:
            new_gearboxes_order.append(self.gearboxes[index])
            new_matrix_mds.append(matrix_mds[index])
        return clusters, cluster_labels_reordered, list_indexes_groups, new_gearboxes_order, new_matrix_mds
        
    def plot_clusters(self):
        colors = [RED, GREEN, ORANGE, BLUE, LIGHTSKYBLUE,
                  ROSE, VIOLET, LIGHTRED, LIGHTGREEN,
                  CYAN, BROWN, GREY, HINT_OF_MINT, GRAVEL]
        all_points = []
        for i, point in enumerate(self.matrix_mds):
            point = {
                'x': point[0], 'y': point[1],
                'Aver path': self.gearboxes_ordered[i].average_path_length,
                'Aver L clutch-input': self.gearboxes_ordered[i].average_clutch_distance,
                'ave_l_ns': self.gearboxes_ordered[i].ave_l_ns,
                'Number shafts': self.gearboxes_ordered[i].number_shafts,
                'Std input_cluches': self.gearboxes_ordered[i].std_clutch_distance,
                'Density': self.gearboxes_ordered[i].density,
                'Cluster': self.labels_reordered[i]
            }
            all_points.append(point)
        
        point_families = []
        for i, indexes in enumerate(self.list_indexes_groups):
            color = colors[i]
            point_family = plot_data.PointFamily(
                point_color=color, point_index=indexes,
                name='Cluster '+str(self.clusters[i])
            )
            point_families.append(point_family)

        all_attributes = ['x', 'y', 'Aver path', 'Aver L clutch-input',
                          'ave_l_ns', 'Number shafts', 'Number gears',
                          'Std input/cluches', 'Density']
        pp_attributes = ['Aver path', 'Number shafts', 'ave_l_ns',
                         'Aver L clutch-input', 'Std input/cluches',
                         'Number  gears', 'Density', 'Cluster']

        tooltip = plot_data.Tooltip(attributes=all_attributes)

        edge_style = plot_data.EdgeStyle(color_stroke=BLACK, dashline=[10, 5])

        plots = [plot_data.Scatter(tooltip=tooltip, x_variable='x',
                                   y_variable='y', elements=all_points)]

        rgbs = [[192, 11, 11], [14, 192, 11], [11, 11, 192]]
        plots.append(plot_data.ParallelPlot(elements=all_points,
                                            edge_style=edge_style,
                                            disposition='vertical',
                                            axes=pp_attributes,
                                            rgbs=rgbs))
        sizes = [plot_data.Window(width=560, height=300),
                 plot_data.Window(width=560, height=300)]
        coords = [(0, 0), (0, 300)]
        clusters = plot_data.MultiplePlots(plots=plots, coords=coords,
                                           sizes=sizes, elements=all_points,
                                           point_families=point_families,
                                           initial_view_on=True)
        return clusters

    def _displays(self, **kwargs):
        plot = self.plot_clusters()
        displays = []
        if 'reference_path' in kwargs:
            reference_path = kwargs['reference_path'] + '/gearboxes_ordered'
        else:
            reference_path = '/gearboxes_ordered'
        display_ = DisplayObject(type_='plot_data', data=plot, 
                                 reference_path=reference_path)
        displays.append(display_.to_dict())
        return displays
