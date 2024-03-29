#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 12:36:10 2020

@author: dumouchel
"""


import tutorials.tutorial5_piping as tuto
# import plot_data.core as plot_data
import volmdlr as vm
from dessia_common.workflow.core import Pipe, Workflow
from dessia_common.workflow.blocks import MethodType, InstantiateModel, MultiPlot, ModelMethod
# from dessia_api_client import Client
import plot_data

f1 = vm.Frame3D(vm.Point3D(0.05, 0.1, 0), vm.Vector3D(1, 0, 0), vm.Vector3D(0, 1, 0), vm.Vector3D(0, 0, 1))
p1 = vm.surfaces.Plane3D(f1)
s1 = vm.surfaces.Surface2D(outer_contour=vm.wires.ClosedPolygon2D([vm.Point2D(-0.05, -0.1),
                                                                vm.Point2D(0.05, -0.1),
                                                                vm.Point2D(0.05, 0.1),
                                                                vm.Point2D(-0.05, 0.1)]),
                        inner_contours=[])
face1 = vm.shells.OpenShell3D([vm.faces.PlaneFace3D(surface3d=p1, surface2d=s1)])
face1.color = (92 / 255, 124 / 255, 172 / 255)
face1.alpha = 1

f2 = vm.Frame3D(vm.Point3D(0.05, 0.1, 0.005), vm.Vector3D(1, 0, 0), vm.Vector3D(0, 0, 1), vm.Vector3D(0, 1, 0))
p2 = vm.surfaces.Plane3D(f2)
s2 = vm.surfaces.Surface2D(outer_contour=vm.wires.ClosedPolygon2D([vm.Point2D(-0.05, -0.005),
                                                                vm.Point2D(0.05, -0.005),
                                                                vm.Point2D(0.05, 0.005),
                                                                vm.Point2D(-0.05, 0.005)]),
                        inner_contours=[])
face2 = vm.shells.OpenShell3D([vm.faces.PlaneFace3D(surface3d=p2, surface2d=s2)])
face2.color = (92 / 255, 124 / 255, 172 / 255)
face2.alpha = 1

vol = vm.core.VolumeModel([face1, face2])
# vol.babylonjs()

housing = tuto.Housing(faces=[face1, face2], origin=vm.Point3D(0, 0, 0))
# housing.babylonjs()

p1 = vm.Point3D(0, 0.1, 0.01)
p2 = vm.Point3D(0.05, 0.1, 0.01)
frame1 = tuto.Frame(start=p1, end=p2)

p1 = vm.Point3D(0.05, 0.1, 0.01)
p2 = vm.Point3D(0.1, 0.1, 0.01)
frame2 = tuto.Frame(start=p1, end=p2)

p1 = vm.Point3D(0, 0.2, 0)
p2 = vm.Point3D(0.05, 0.2, 0)
frame3 = tuto.Frame(start=p1, end=p2)

p1 = vm.Point3D(0.05, 0.2, 0)
p2 = vm.Point3D(0.1, 0.2, 0)
frame4 = tuto.Frame(start=p1, end=p2)

p1 = vm.Point3D(0, 0, 0)
p2 = vm.Point3D(0.1, 0, 0)
piping1 = tuto.Piping(start=p1, end=p2,
                      direction_start=vm.Vector3D(0, 0, 1), direction_end=vm.Vector3D(1, 0, 1),
                      diameter=0.005, length_connector=0.1, minimum_radius=0.03)
piping2 = tuto.Piping(start=p1, end=p2,
                      direction_start=vm.Vector3D(0, 0, 1), direction_end=vm.Vector3D(1, 0, 1),
                      diameter=0.005, length_connector=0.1, minimum_radius=0.05)

assemblies = []
minimum_radius = 0.02
for i in range(30):
    minimum_radius += 0.003
    p1 = vm.Point3D(0, 0, 0)
    p2 = vm.Point3D(0.1, 0, 0)
    for j in range(2):
        p1 += vm.Point3D(0.01, 0, 0)
        piping1 = tuto.Piping(start=p1, end=p2,
                              direction_start=vm.Vector3D(0, 0, 1), direction_end=vm.Vector3D(1, 0, 1),
                              diameter=0.005, length_connector=0.1, minimum_radius=0.03)
        assemblies.append(tuto.Assembly(frames=[frame1, frame3, frame4, frame2], piping=piping1, housing=housing))


block_optimizer = InstantiateModel(tuto.Optimizer, name='Optimizer')


block_optimize = ModelMethod(method_type=MethodType(tuto.Optimizer, 'optimize'), name='Optimize')

list_attribute1 = ['length', 'min_radius', 'max_radius', 'distance_input', 'straight_line']
display_reductor = MultiPlot(selector_name="Multiplot", attributes=list_attribute1, name='Display')

block_workflow = [block_optimizer, block_optimize, display_reductor]

pipe_worflow = [Pipe(block_optimizer.outputs[0], block_optimize.inputs[0]),
                Pipe(block_optimize.outputs[0], display_reductor.inputs[0])]

workflow = Workflow(block_workflow, pipe_worflow, block_optimize.outputs[0], name="workflow pipe")
workflow.plot()

input_values = {workflow.input_index(block_optimize.inputs[1]): assemblies,
                workflow.input_index(block_optimize.inputs[2]): 1,
                }

workflow_run = workflow.run(input_values)
solution = workflow_run.output_value[0]
solution.babylonjs()

# c = Client(api_url='https://api.platform-dev.dessia.tech')
# r = c.create_object_from_python_object(workflow_run)
