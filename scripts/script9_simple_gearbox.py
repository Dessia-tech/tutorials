# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 11:29:57 2021

@author: wiraj
"""
import tutorials.tutorial9_simple_gearbox as objects
import numpy as np
import plot_data
import pandas as pd
from dessia_api_client import Client

"""
Engine efficiency map
"""
engine_speeds = list(np.linspace(500, 6000, num = 12)) #Engine speed in rpm
engine_speeds = [float(i)*np.pi/30 for i in engine_speeds]  # in rad/s
engine_torques = [15.6,31.2, 46.8, 62.4, 78, 93.6, 109.2, 124.8, 140.4, 156, 171.6] #engine torque in N*m
mass_flow_rate = [[0.1389, 0.2009, 0.2524, 0.3006, 0.3471, 0.4264, 0.4803, 0.5881, 0.5881, 0.6535, 0.7188],
                  [0.2777, 0.3659, 0.4582, 0.5587, 0.6453, 0.7792, 0.8977, 1.0325, 1.1762, 1.3069, 1.4376],
                  [0.4166, 0.5538, 0.7057, 0.8332, 0.9557, 1.0733, 1.2127, 1.3428, 1.5438, 1.9604, 2.1564],
                  [0.5391, 0.7188, 0.9116, 1.0913, 1.2497, 1.4115, 1.5552, 1.7774, 2.0290, 2.3851, 2.8752],
                  [0.6330, 0.8658, 1.0904, 1.2906, 1.5111, 1.6786, 1.9440, 2.2217, 2.4995, 2.8997, 3.5940],
                  [0.7106, 0.9949, 1.2718, 1.5193, 1.7888, 2.0878, 2.3671, 2.6661, 2.9993, 3.5286, 4.3128],
                  [0.7433, 1.0806, 1.3722, 1.7839, 2.2013, 2.5490, 2.8817, 3.1562, 3.5507, 4.1739, 5.0316],
                  [0.9475, 1.2938, 1.7290, 2.2087, 2.5648, 2.9993, 3.3391, 3.6855, 4.2932, 4.8355, 5.7504],
                  [1.1027, 1.6026, 2.1525, 2.5877, 2.9957, 3.4184, 3.8852, 4.4108, 5.0151, 5.6238, 6.4692],
                  [1.5519, 2.0910, 2.5730, 3.0222, 3.4715, 3.8717, 4.4998, 5.0642, 5.7781, 6.4528, 7.1880],
                  [1.8868, 2.5517, 3.1537, 3.6479, 4.0882, 4.4206, 5.2203, 5.8941, 6.5500, 7.2329, 7.9068],
                  [2.0584, 2.8817, 3.5286, 4.0775, 4.5578, 5.1165, 5.6948, 6.4300, 7.1455, 7.8414, 8.6256]] #mass flow rate in g/s
mass_flow_rate_kgps = []
for list_mass_flow_rate in mass_flow_rate:
    list_mass_flow = []
    for mass_flow in list_mass_flow_rate:
        list_mass_flow.append(mass_flow/1000)                                                                #mass flow rate in kg/s
    mass_flow_rate_kgps.append(list_mass_flow) 
    

fuel_hv = 0.012068709                                                       # in kWh/g
fuel_hv = fuel_hv*3.6e9                                                    # in J/kg
efficiency_map = objects.EfficiencyMap(engine_speeds = engine_speeds, engine_torques = engine_torques, mass_flow_rate = mass_flow_rate_kgps, fuel_hv = fuel_hv)


"""
WLTP cycle
"""

cycle_speeds= [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.2,3.1,5.7,8.0,10.1,12.0,13.8,15.4,16.7,17.7,18.3,18.8,
                18.9,18.4,16.9,14.3,10.8,7.1,4.0,0.0,0.0,0.0,0.0,1.5,3.8,5.6,7.5,9.2,10.8,12.4,13.8,15.2,16.3,17.3,18.0,
                18.8,19.5,20.2,20.9,21.7,22.4,23.1,23.7,24.4,25.1,25.4,25.2,23.4,21.8,19.7,17.3,14.7,12.0,9.4,5.6,3.1,0.0,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.7,1.1,1.9,2.5,3.5,4.7,6.1,7.5,9.4,11.0,12.9,14.5,
                16.4,18.0,20.0,21.5,23.5,25.0,26.8,28.2,30.0,31.4,32.5,33.2,33.4,33.7,33.9,34.2,34.4,34.7,34.9,35.2,35.4,
                35.7,35.9,36.6,37.5,38.4,39.3,40.0,40.6,41.1,41.4,41.6,41.8,41.8,41.9,41.9,42.0,42.0,42.2,42.3,42.6,43.0,
                43.3,43.7,44.0,44.3,44.5,44.6,44.6,44.5,44.4,44.3,44.2,44.1,44.0,43.9,43.8,43.7,43.6,43.5,43.4,43.3,43.1,
                42.9,42.7,42.5,42.3,42.2,42.2,42.2,42.3,42.4,42.5,42.7,42.9,43.1,43.2,43.3,43.4,43.4,43.2,42.9,42.6,42.2,
                41.9,41.5,41.0,40.5,39.9,39.3,38.7,38.1,37.5,36.9,36.3,35.7,35.1,34.5,33.9,33.6,33.5,33.6,33.9,34.3,34.7,
                35.1,35.5,35.9,36.4,36.9,37.4,37.9,38.3,38.7,39.1,39.3,39.5,39.7,39.9,40.0,40.1,40.2,40.3,40.4,40.5,40.5,
                40.4,40.3,40.2,40.1,39.7,38.8,37.4,35.6,33.4,31.2,29.1,27.6,26.6,26.2,26.3,26.7,27.5,28.4,29.4,30.4,31.2,
                31.9,32.5,33.0,33.4,33.8,34.1,34.3,34.3,33.9,33.3,32.6,31.8,30.7,29.6,28.6,27.8,27.0,26.4,25.8,25.3,24.9,
                24.5,24.2,24.0,23.8,23.6,23.5,23.4,23.3,23.3,23.2,23.1,23.0,22.8,22.5,22.1,21.7,21.1,20.4,19.5,18.5,17.6,
                16.6,15.7,14.9,14.3,14.1,14.0,13.9,13.8,13.7,13.6,13.5,13.4,13.3,13.2,13.2,13.2,13.4,13.5,13.7,13.8,14.0,
                14.1,14.3,14.4,14.4,14.4,14.3,14.3,14.0,13.0,11.4,10.2,8.0,7.0,6.0,5.5,5.0,4.5,4.0,3.5,3.0,2.5,2.0,1.5,
                1.0,0.5,0.0,0.0,0.0,0.0,0.0,0.0,2.2,4.5,6.6,8.6,10.6,12.5,14.4,16.3,17.9,19.1,19.9,20.3,20.5,20.7,21.0,
                21.6,22.6,23.7,24.8,25.7,26.2,26.4,26.4,26.4,26.5,26.6,26.8,26.9,27.2,27.5,28.0,28.8,29.9,31.0,31.9,32.5,
                32.6,32.4,32.0,31.3,30.3,28.0,27.0,24.0,22.5,19.0,17.5,14.0,12.5,9.0,7.5,4.0,2.9,0.0,0.0,0.0,0.0,0.0,0.0,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.6,3.1,4.6,6.1,7.8,9.5,11.3,13.2,15.0,16.8,18.4,20.1,21.6,23.1,24.6,
                26.0,27.5,29.0,30.6,32.1,33.7,35.3,36.8,38.1,39.3,40.4,41.2,41.9,42.6,43.3,44.0,44.6,45.3,45.5,45.5,45.2,
                44.7,44.2,43.6,43.1,42.8,42.7,42.8,43.3,43.9,44.6,45.4,46.3,47.2,47.8,48.2,48.5,48.7,48.9,49.1,49.1,49.0,
                48.8,48.6,48.5,48.4,48.3,48.2,48.1,47.5,46.7,45.7,44.6,42.9,40.8,38.2,35.3,31.8,28.7,25.8,22.9,20.2,17.3,
                15.0,12.3,10.3,7.8,6.5,4.4,3.2,1.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,1.9,2.7,5.2,7.0,9.6,11.4,14.1,15.8,
                18.2,19.7,21.8,23.2,24.7,25.8,26.7,27.2,27.7,28.1,28.4,28.7,29.0,29.2,29.4,29.4,29.3,28.9,28.5,28.1,27.6,
                26.9,26.0,24.6,22.8,21.0,19.5,18.6,18.4,19.0,20.1,21.5,23.1,24.9,26.4,27.9,29.2,30.4,31.6,32.8,34.0,35.1,
                36.3,37.4,38.6,39.6,40.6,41.6,42.4,43.0,43.6,44.0,44.4,44.8,45.2,45.6,46.0,46.5,47.0,47.5,48.0,48.6,49.1,
                49.7,50.2,50.8,51.3,51.8,52.3,52.9,53.4,54.0,54.5,55.1,55.6,56.2,56.7,57.3,57.9,58.4,58.8,58.9,58.4,58.1,
                57.6,56.9,56.3,55.7,55.3,55.0,54.7,54.5,54.4,54.3,54.2,54.1,53.8,53.5,53.0,52.6,52.2,51.9,51.7,51.7,51.8,
                52.0,52.3,52.6,52.9,53.1,53.2,53.3,53.3,53.4,53.5,53.7,54.0,54.4,54.9,55.6,56.3,57.1,57.9,58.8,59.6,60.3,
                60.9,61.3,61.7,61.8,61.8,61.6,61.2,60.8,60.4,59.9,59.4,58.9,58.6,58.2,57.9,57.7,57.5,57.2,57.0,56.8,56.6,
                56.6,56.7,57.1,57.6,58.2,59.0,59.8,60.6,61.4,62.2,62.9,63.5,64.2,64.4,64.4,64.0,63.5,62.9,62.4,62.0,61.6,
                61.4,61.2,61.0,60.7,60.2,59.6,58.9,58.1,57.2,56.3,55.3,54.4,53.4,52.4,51.4,50.4,49.4,48.5,47.5,46.5,45.4,
                44.3,43.1,42.0,40.8,39.7,38.8,38.1,37.4,37.1,36.9,37.0,37.5,37.8,38.2,38.6,39.1,39.6,40.1,40.7,41.3,41.9,
                42.7,43.4,44.2,45.0,45.9,46.8,47.7,48.7,49.7,50.6,51.6,52.5,53.3,54.1,54.7,55.3,55.7,56.1,56.4,56.7,57.1,
                57.5,58.0,58.7,59.3,60.0,60.6,61.3,61.5,61.5,61.4,61.2,60.5,60.0,59.5,58.9,58.4,57.9,57.5,57.1,56.7,56.4,
                56.1,55.8,55.5,55.3,55.0,54.7,54.4,54.2,54.0,53.9,53.7,53.6,53.5,53.4,53.3,53.2,53.1,53.0,53.0,53.0,53.0,
                53.0,53.0,52.8,52.5,51.9,51.1,50.2,49.2,48.2,47.3,46.4,45.6,45.0,44.3,43.8,43.3,42.8,42.4,42.0,41.6,41.1,
                40.3,39.5,38.6,37.7,36.7,36.2,36.0,36.2,37.0,38.0,39.0,39.7,40.2,40.7,41.2,41.7,42.2,42.7,43.2,43.6,44.0,
                44.2,44.4,44.5,44.6,44.7,44.6,44.5,44.4,44.2,44.1,43.7,43.3,42.8,42.3,41.6,40.7,39.8,38.8,37.8,36.9,36.1,
                35.5,35.0,34.7,34.4,34.1,33.9,33.6,33.3,33.0,32.7,32.3,31.9,31.5,31.0,30.6,30.2,29.7,29.1,28.4,27.6,26.8,
                26.0,25.1,24.2,23.3,22.4,21.5,20.6,19.7,18.8,17.7,16.4,14.9,13.2,11.3,9.4,7.5,5.6,3.7,1.9,1.0,0.0,0.0,0.0
                ,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.2,3.1,5.7,8.0,10.1,12.0,13.8
                ,15.4,16.7,17.7,18.3,18.8,18.9,18.4,16.9,14.3,10.8,7.1,4.0,0.0,0.0,0.0,0.0,1.5,3.8,5.6,7.5,9.2,10.8,12.4,
                13.8,15.2,16.3,17.3,18.0,18.8,19.5,20.2,20.9,21.7,22.4,23.1,23.7,24.4,25.1,25.4,25.2,23.4,21.8,19.7,17.3,
                14.7,12.0,9.4,5.6,3.1,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.7,1.1,1.9,2.5,3.5,4.7,
                6.1,7.5,9.4,11.0,12.9,14.5,16.4,18.0,20.0,21.5,23.5,25.0,26.8,28.2,30.0,31.4,32.5,33.2,33.4,33.7,33.9,
                34.2,34.4,34.7,34.9,35.2,35.4,35.7,35.9,36.6,37.5,38.4,39.3,40.0,40.6,41.1,41.4,41.6,41.8,41.8,41.9,41.9,
                42.0,42.0,42.2,42.3,42.6,43.0,43.3,43.7,44.0,44.3,44.5,44.6,44.6,44.5,44.4,44.3,44.2,44.1,44.0,43.9,43.8,
                43.7,43.6,43.5,43.4,43.3,43.1,42.9,42.7,42.5,42.3,42.2,42.2,42.2,42.3,42.4,42.5,42.7,42.9,43.1,43.2,43.3,
                43.4,43.4,43.2,42.9,42.6,42.2,41.9,41.5,41.0,40.5,39.9,39.3,38.7,38.1,37.5,36.9,36.3,35.7,35.1,34.5,33.9,
                33.6,33.5,33.6,33.9,34.3,34.7,35.1,35.5,35.9,36.4,36.9,37.4,37.9,38.3,38.7,39.1,39.3,39.5,39.7,39.9,40.0,
                40.1,40.2,40.3,40.4,40.5,40.5,40.4,40.3,40.2,40.1,39.7,38.8,37.4,35.6,33.4,31.2,29.1,27.6,26.6,26.2,26.3,
                26.7,27.5,28.4,29.4,30.4,31.2,31.9,32.5,33.0,33.4,33.8,34.1,34.3,34.3,33.9,33.3,32.6,31.8,30.7,29.6,28.6,
                27.8,27.0,26.4,25.8,25.3,24.9,24.5,24.2,24.0,23.8,23.6,23.5,23.4,23.3,23.3,23.2,23.1,23.0,22.8,22.5,22.1,
                21.7,21.1,20.4,19.5,18.5,17.6,16.6,15.7,14.9,14.3,14.1,14.0,13.9,13.8,13.7,13.6,13.5,13.4,13.3,13.2,13.2,
                13.2,13.4,13.5,13.7,13.8,14.0,14.1,14.3,14.4,14.4,14.4,14.3,14.3,14.0,13.0,11.4,10.2,8.0,7.0,6.0,5.5,5.0,
                4.5,4.0,3.5,3.0,2.5,2.0,1.5,1.0,0.5,0.0,0.0,0.0,0.0,0.0,0.0,2.2,4.5,6.6,8.6,10.6,12.5,14.4,16.3,17.9,19.1,
                19.9,20.3,20.5,20.7,21.0,21.6,22.6,23.7,24.8,25.7,26.2,26.4,26.4,26.4,26.5,26.6,26.8,26.9,27.2,27.5,28.0,
                28.8,29.9,31.0,31.9,32.5,32.6,32.4,32.0,31.3,30.3,28.0,27.0,24.0,22.5,19.0,17.5,14.0,12.5,9.0,7.5,4.0,
                2.9,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
                ,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.6,3.1,4.6,6.1,7.8,9.5,11.3,13.2,15.0,
                16.8,18.4,20.1,21.6,23.1,24.6,26.0,27.5,29.0,30.6,32.1,33.7,35.3,36.8,38.1,39.3,40.4,41.2,41.9,42.6,43.3,
                44.0,44.6,45.3,45.5,45.5,45.2,44.7,44.2,43.6,43.1,42.8,42.7,42.8,43.3,43.9,44.6,45.4,46.3,47.2,47.8,48.2,
                48.5,48.7,48.9,49.1,49.1,49.0,48.8,48.6,48.5,48.4,48.3,48.2,48.1,47.5,46.7,45.7,44.6,42.9,40.8,38.2,35.3,
                31.8,28.7,25.8,22.9,20.2,17.3,15.0,12.3,10.3,7.8,6.5,4.4,3.2,1.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]        # velocity in km/h



car_mass = 1524                                                             # Midsize car wheight in kilograms
dt = 1                                                                      # time interval in seconds
tire_radius = 0.1905                                                        # tire radius in m
cycle_speeds = [speed*1000/3600 for speed in cycle_speeds] #cycle speed in m/s
wltp_cycle = objects.WLTPCycle(cycle_speeds = cycle_speeds, car_mass = car_mass, tire_radius = tire_radius)


"""
Engine 
"""
setpoint_speed = 600*np.pi/30 # in rad/s
setpoint_torque = 100
engine = objects.Engine(efficiency_map = efficiency_map, setpoint_speed = setpoint_speed, setpoint_torque = setpoint_torque)

"""
Gearbox
"""
speed_ranges = [[0, 30], [20 ,40], [30,50], [45, 70]] # in km/h
speed_ranges = [[speed_range[0]*(1000*2*np.pi)/(3600*np.pi*tire_radius), speed_range[1]*(1000*2*np.pi)/(3600*np.pi*tire_radius)] for speed_range in speed_ranges] #in rad/s
gearbox = objects.GearBox(engine = engine, speed_ranges = speed_ranges)
# gearbox_results = objects.GearBoxResults(gearbox, wltp_cycle)

"""
GearBox Optimizer
"""

optimizer = objects.GearBoxOptimizer(gearbox = gearbox, wltp_cycle = wltp_cycle, first_gear_ratio_min_max = [.5, 4.5])
"""
Results
"""

results = optimizer.optimize(1)
for result in results:
    print('Ratios: ',result.gearbox.ratios)
    plot_data.plot_canvas(plot_data_object = result.plot_data()[0], canvas_id = 'canvas')
    plot_data.plot_canvas(plot_data_object = result.plot_data()[1], canvas_id = 'canvas')
    
        
# c = Client(api_url = 'https://api.demo.dessia.tech')
# r = c.create_object_from_python_object(results[0])