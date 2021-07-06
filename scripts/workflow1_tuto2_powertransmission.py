#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 12:36:10 2020

@author: launay
"""
import tutorials.tutorial2_powertransmission as objects
import dessia_common.workflow as wf
import dessia_common.typings as typings
from dessia_api_client import Client

block_optimizer = wf.InstanciateModel(objects.Optimizer, name='Optimizer')
block_optimize = wf.ModelMethod(typings.MethodType(objects.Optimizer, 'optimize'), name='Optimize')

block_instanciate_reductor = wf.InstanciateModel(objects.InstanciateReductor, name='Instanciate Reductor')
block_instanciate = wf.ModelMethod(typings.MethodType(objects.InstanciateReductor, 'instanciate'), name='Instanciate')

block_motor = wf.InstanciateModel(objects.Motor, name='Motor')

list_attribute1 = ['mass_reductor', 'number_solution']
display_reductor = wf.MultiPlot(list_attribute1, 1, name='Display Reductor')

block_workflow = [block_optimizer, block_optimize, block_instanciate_reductor, block_instanciate, block_motor,
                  display_reductor]

pipe_worflow = [wf.Pipe(block_optimizer.outputs[0], block_optimize.inputs[0]),
                wf.Pipe(block_instanciate_reductor.outputs[0], block_instanciate.inputs[0]),
                wf.Pipe(block_motor.outputs[0], block_instanciate_reductor.inputs[0]),
                wf.Pipe(block_instanciate.outputs[0], block_optimizer.inputs[0]),
                wf.Pipe(block_optimize.outputs[0], display_reductor.inputs[0])]

workflow = wf.Workflow(block_workflow, pipe_worflow, block_optimize.outputs[0])

input_values = {workflow.index(block_optimizer.inputs[1]): 500,
                workflow.index(block_optimizer.inputs[2]): [-1, 1],
                workflow.index(block_optimizer.inputs[3]): [-1, 1],

                workflow.index(block_instanciate_reductor.inputs[1]): 0.01,

                workflow.index(block_motor.inputs[0]): 0.1,
                workflow.index(block_motor.inputs[1]): 0.2,
                workflow.index(block_motor.inputs[2]): 150

                }

workflow_generator_run = workflow.run(input_values)

c = Client(api_url='https://api.platform-dev.dessia.tech')
r = c.create_object_from_python_object(workflow_generator_run)
