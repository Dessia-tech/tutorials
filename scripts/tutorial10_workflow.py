#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 13:11:55 2021

@author: dasilva
"""
import tutorials.tutorial10 as objects
import dessia_common.workflow as wf

from dessia_api_client import Client
import numpy as np

block_generator = wf.InstanciateModel(objects.GearBoxGenerator, name = 'Gearbox Generator')
block_generate = wf.ModelMethod(objects.GearBoxGenerator, 'generate', name = 'Generate')
block_efficiencymap = wf.InstanciateModel(objects.EfficiencyMap, name= 'Efficiency Map')
block_engine = wf.InstanciateModel(objects.Engine, name= 'Engine')
block_gearbox = wf.InstanciateModel(objects.GearBox, name='Gearbox')
block_cluster = wf.InstanciateModel(objects.Clustering, name = 'Clustering')


display = wf.Display()






block_workflow = [block_generator, block_generate, block_gearbox, block_engine, block_efficiencymap,
                  # block_wltpcycle,
                  block_cluster,
                    display
                  ]
pipe_workflow = [wf.Pipe(block_generator.outputs[0], block_generate.inputs[0]), 
                  wf.Pipe(block_gearbox.outputs[0], block_generator.inputs[0]), 
                  wf.Pipe(block_engine.outputs[0], block_gearbox.inputs[0]), 
                  wf.Pipe(block_efficiencymap.outputs[0], block_engine.inputs[0]),
                   wf.Pipe(block_generate.outputs[0], block_cluster.inputs[0]),
                   wf.Pipe(block_cluster.outputs[0], display.inputs[0])
                  ]

workflow = wf.Workflow(block_workflow, pipe_workflow, block_generate.outputs[0])




engine_speeds = list(np.linspace(500, 6000, num = 12)) #Engine speed in rpm
engine_speeds = [float(i)*(np.pi/30) for i in engine_speeds]  # in rad/s
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


cycle_speeds= [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.2,3.1,5.7,8.0,10.1,12.0,13.8,15.4,16.7,17.7,18.3,18.8,
                18.9,18.4,16.9,14.3,10.8,7.1,4.0,0.0,0.0,0.0,0.0,1.5,3.8,5.6,7.5,9.2,10.8,12.4,13.8,15.2,16.3,17.3,18.0,
                18.8,19.5,20.2,20.9,21.7]        # velocity in km/h

car_mass = 1524                                                             # Midsize car wheight in kilograms
dt = 1                                                                      # time interval in seconds
tire_radius = 0.1905                                                        # tire radius in m
cycle_speeds = [speed*1000/3600 for speed in cycle_speeds] #cycle speed in m/s
setpoint_speed = 600*(np.pi/30) # in rad/s
setpoint_torque = 100
speed_ranges = [[0, 30], [20 ,40], [30,50]] # in km/h
speed_ranges = [[speed_range[0]*(1000*2)/(3600*tire_radius), speed_range[1]*(1000*2)/(3600*tire_radius)] for speed_range in speed_ranges] #in rad/s

number_inputs = 2
number_shaft_assemblies=5
max_number_gears = 5

input_values = {workflow.index(block_generator.inputs[1]): 2,
                workflow.index(block_generator.inputs[2]): 5,
                workflow.index(block_generator.inputs[3]): 5, 
                workflow.index(block_gearbox.inputs[1]):speed_ranges, 
                workflow.index(block_engine.inputs[1]):setpoint_speed,
                workflow.index(block_engine.inputs[2]):setpoint_torque,
                workflow.index(block_efficiencymap.inputs[0]):engine_speeds,
                workflow.index(block_efficiencymap.inputs[1]):engine_torques, 
                workflow.index(block_efficiencymap.inputs[2]):mass_flow_rate_kgps, 
                workflow.index(block_efficiencymap.inputs[3]):fuel_hv, 
                # workflow.index(block_wltpcycle.inputs[0]):cycle_speeds, 
                # workflow.index(block_wltpcycle.inputs[1]):car_mass, 
                # workflow.index(block_wltpcycle.inputs[2]):tire_radius
                }

workflow_run = workflow.run(input_values)


d1 = workflow_run.to_dict()
obj = wf.WorkflowRun.dict_to_object(d1)
import json
object1=json.dumps(d1)
object2=json.loads(object1)

c = Client(api_url = 'https://api.platform-dev.dessia.tech')
r = c.create_object_from_python_object(workflow_run)
