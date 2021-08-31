#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 12:36:10 2020

@author: launay
"""
import tutorials.tutorial1_rivetedassembly as tuto
import plot_data.core as plot_data
import volmdlr as vm
from dessia_api_client import Client
import dessia_common.workflow as wf

block_generator = wf.InstanciateModel(tuto.Generator, name='Generator')

generate_method = wf.MethodType(class_=tuto.Generator, name='generate')
block_generate = wf.ModelMethod(method_type=generate_method, name='generate')

list_attribute1 = ['number_rivet1', 'number_rivet2', 'number_rivet', 'mass', 'pressure_applied', 'fatigue_resistance']
display_reductor = wf.MultiPlot(list_attribute1, 1, name='Display Reductor')

block_workflow = [block_generator, block_generate, display_reductor]

pipe_worflow = [wf.Pipe(block_generator.outputs[0], block_generate.inputs[0]),
                wf.Pipe(block_generate.outputs[0], display_reductor.inputs[0])]

workflow = wf.Workflow(block_workflow, pipe_worflow, block_generate.outputs[0])

p1 = tuto.Panel(1, 1, 0.01)
p2 = tuto.Panel(1.1, 1, 0.01)
r1 = tuto.Rivet(0.01, 0.05, 0.012, 0.005)
pc1 = tuto.PanelCombination([p1, p2], [vm.Point3D(0, 0, 0), vm.Point3D(0.7, 0.2, 0.01)])
rule1 = tuto.Rule(0.1, 0.2)


input_values = {workflow.index(block_generator.inputs[0]): pc1,
                workflow.index(block_generator.inputs[1]): r1,
                workflow.index(block_generator.inputs[2]): rule1,
                }

workflow_run = workflow.run(input_values)
solution = workflow_run.output_value[0]
plot_data.plot_canvas(solution.plot_data()[0], canvas_id='canvas')

# c = Client(api_url='https://api.platform-dev.dessia.tech')
# r = c.create_object_from_python_object(workflow_run)
