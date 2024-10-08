#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 21:32:30 2019

@author: jezequel
"""
import copy
import math
from typing import List, Tuple

import dectree as dt

import numpy as npy
import plot_data
import volmdlr as vm
from volmdlr.core import VolumeModel
from volmdlr.shapes import Solid
import volmdlr.primitives3d as p3d
from dessia_common.core import DessiaObject, PhysicalObject
from dessia_common.decorators import plot_data_view, cad_view
from scipy.optimize import minimize

# =============================================================================


class Shaft(DessiaObject):
    _eq_is_data_eq = False

    def __init__(self, pos_x: float, pos_y: float, length: float, name: str = ''):
        self.pos_x = pos_x
        self.pos_y = pos_y

        self.length = length
        self.diameter = 0.04
        self.z_position = self.length / 2
        DessiaObject.__init__(self, name=name)

    @plot_data_view(selector='Shaft')
    def plot_data(self):
        plot_datas = []
        center = vm.Point2D(self.pos_x, self.pos_y)
        circle = vm.curves.Circle2D.from_center_and_radius(center=center, radius=self.diameter / 2)
        plot_datas.append(circle.plot_data())

        return plot_data.PrimitiveGroup(primitives=plot_datas)

    @cad_view("Shaft CAD")
    def cad_view(self):
        return VolumeModel(self.volmdlr_primitives()).babylon_data()

    def volmdlr_primitives(self):
        primitives = []
        pos = vm.Point3D(self.pos_x, self.pos_y, self.z_position)
        axis = vm.Vector3D(0, 0, 1)
        cylinder = Solid.make_cylinder(radius=self.diameter / 2,
                                       height=self.length,
                                       frame=vm.Frame3D(pos - self.length / 2 * axis, vm.X3D, vm.Y3D, vm.Z3D))
        primitives.append(cylinder)
        return primitives

    def mass(self):
        return 7500 * math.pi * self.length * (self.diameter / 2) ** 2


# =============================================================================


class Motor(DessiaObject):

    def __init__(self, diameter: float, length: float, speed: float, name: str = ''):
        self.diameter = diameter
        self.length = length
        self.speed = speed

        DessiaObject.__init__(self, name=name)
        self.z_position = self.length / 2
        self.pos_x = 0
        self.pos_y = 0

    @plot_data_view(selector="Motor")
    def plot_data(self):
        plot_datas = []
        center = vm.Point2D(self.pos_x, self.pos_y)
        circle = vm.curves.Circle2D.from_center_and_radius(center=center, radius=self.diameter / 2)
        plot_datas.append(circle.plot_data())

        return plot_data.PrimitiveGroup(primitives=plot_datas)

    @cad_view("Motor CAD")
    def cad_view(self):
        return VolumeModel(self.volmdlr_primitives()).babylon_data()

    def volmdlr_primitives(self):
        primitives = []
        pos = vm.Point3D(self.pos_x, self.pos_y, self.z_position)
        axis = vm.Vector3D(0, 0, 1)
        cylinder = Solid.make_cylinder(radius=self.diameter / 2,
                                       height=self.length,
                                       frame=vm.Frame3D(pos - self.length / 2 * axis, vm.X3D, vm.Y3D, vm.Z3D))
        primitives.append(cylinder)
        return primitives


# =============================================================================


class Gear(DessiaObject):
    _eq_is_data_eq = False

    def __init__(self, z: int, length: float, shaft: Shaft, module: float = 0.01, name: str = ''):
        self.z = z
        self.length = length
        self.shaft = shaft
        self.module = module
        self.diameter = z * module
        DessiaObject.__init__(self, name=name)
        self.z_position = 0

    @plot_data_view(selector="Gear")
    def plot_data(self):
        plot_datas = []
        center = vm.Point2D(self.shaft.pos_x, self.shaft.pos_y)
        circle = vm.curves.Circle2D.from_center_and_radius(center=center, radius=self.diameter / 2)
        plot_datas.append(circle.plot_data())

        return plot_data.PrimitiveGroup(primitives=plot_datas)

    @cad_view("Gear CAD")
    def cad_view(self):
        return VolumeModel(self.volmdlr_primitives()).babylon_data()

    def volmdlr_primitives(self):
        primitives = []
        pos = vm.Point3D(self.shaft.pos_x, self.shaft.pos_y, self.z_position)
        axis = vm.Vector3D(0, 0, 1)
        cylinder = Solid.make_cylinder(radius=self.diameter / 2,
                                       height=self.length,
                                       frame=vm.Frame3D(pos - self.length / 2 * axis, vm.X3D, vm.Y3D, vm.Z3D))
        primitives.append(cylinder)
        return primitives

    def mass(self):
        return 7500 * math.pi * self.length * (self.diameter / 2) ** 2

    def update_diameter(self):
        self.diameter = self.z * self.module


# =============================================================================


class Mesh(DessiaObject):

    def __init__(self, gear1: Gear, gear2: Gear, name: str = ''):
        self.gear1 = gear1
        self.gear2 = gear2
        self.gears = [gear1, gear2]
        DessiaObject.__init__(self, name=name)


# =============================================================================


class Reductor(PhysicalObject):
    _standalone_in_db = True

    def __init__(self, motor: Motor, shafts: List[Shaft], meshes: List[Mesh], number_solution: int = 0, name: str = ''):
        self.shafts = shafts
        self.meshes = meshes
        self.motor = motor
        self.offset = 0.02
        self.number_solution = number_solution
        DessiaObject.__init__(self, name=name)
        self.mass_reductor = self.mass()

    def speed_output(self):

        output_speed = self.motor.speed
        for mesh in self.meshes:
            output_speed = output_speed * mesh.gear1.z / mesh.gear2.z
        return output_speed

    def update(self, x):
        i = 0

        for shaft in self.shafts:
            shaft.pos_x = x[i]
            shaft.pos_y = x[i + 1]

            i += 2
        for mesh in self.meshes:

            shaft_gear1 = mesh.gear1.shaft
            shaft_gear2 = mesh.gear2.shaft
            center_distance = ((shaft_gear1.pos_x - shaft_gear2.pos_x) ** 2 + (
                    shaft_gear1.pos_y - shaft_gear2.pos_y) ** 2) ** (1 / 2)
            mesh.gear1.diameter = 2 * center_distance * mesh.gear1.z / (mesh.gear1.z + mesh.gear2.z)
            mesh.gear2.diameter = 2 * center_distance * mesh.gear2.z / (mesh.gear1.z + mesh.gear2.z)
            mesh.gear1.module = mesh.gear1.diameter / mesh.gear1.z
            mesh.gear2.module = mesh.gear1.module

        self.mass_reductor = self.mass()

    @plot_data_view(selector="Reductor")
    def plot_data(self):
        plot_datas = []

        self.motor.pos_x = self.shafts[0].pos_x
        self.motor.pos_y = self.shafts[0].pos_y
        plot_datas.extend(self.motor.plot_data().primitives)
        for shaft in self.shafts:
            plot_datas.extend(shaft.plot_data().primitives)
        for meshe in self.meshes:
            plot_datas.extend(meshe.gear1.plot_data().primitives)
            plot_datas.extend(meshe.gear2.plot_data().primitives)
        plot_data_sorted = sorted(plot_datas, key=lambda plot_data: plot_data.r)

        return plot_data.PrimitiveGroup(primitives=plot_data_sorted[::-1])

    @cad_view("Reductor CAD")
    def cad_view(self):
        return VolumeModel(self.volmdlr_primitives()).babylon_data()

    def volmdlr_primitives(self):
        primitives = []
        self.motor.pos_x = self.shafts[0].pos_x
        self.motor.pos_y = self.shafts[0].pos_y

        primitives.extend(self.motor.volmdlr_primitives())
        z_previous_position_gear = self.motor.length + self.offset
        z_previous_position_shaft = 0
        for shaft in self.shafts:
            z_position = z_previous_position_gear
            for mesh in self.meshes:
                if mesh.gear1.shaft == shaft:
                    z_position = z_previous_position_gear + mesh.gear1.length / 2
                    mesh.gear1.z_position = z_position
                    mesh.gear2.z_position = z_position
                    primitives.extend(mesh.gear1.volmdlr_primitives())
                    primitives.extend(mesh.gear2.volmdlr_primitives())
                    break

            shaft.length = (z_position + mesh.gear1.length / 2 + self.offset - z_previous_position_shaft)
            shaft.z_position = shaft.length / 2 + z_previous_position_shaft

            primitives.extend(shaft.volmdlr_primitives())

            z_previous_position_gear = (z_position + mesh.gear2.length / 2 + self.offset)
            z_previous_position_shaft = (z_position - mesh.gear2.length / 2 - self.offset)
        return primitives

    def mass(self):
        mass = 0
        for shaft in self.shafts:
            mass += shaft.mass()
        for meshe in self.meshes:
            for gear in [meshe.gear1, meshe.gear2]:
                mass += gear.mass()
        return mass


class Optimizer(DessiaObject):
    def __init__(self, reductor: Reductor, x_min_max: Tuple[float, float],
                 y_min_max: Tuple[float, float], name: str = ''):
        self.reductor = reductor
        self.x_min_max = x_min_max
        self.y_min_max = y_min_max

        DessiaObject.__init__(self, name=name)

        bounds = []
        for shaft in reductor.shafts:
            bounds.append([x_min_max[0], x_min_max[1]])
            bounds.append([y_min_max[0], y_min_max[1]])

        self.bounds = bounds

    def objective(self, x):
        self.reductor.update(x)
        speed = self.reductor.speed_output()
        functional = 0

        previous_radius_gear_1 = 0
        previous_radius_gear_2 = 0
        previus_radius_shaft = 0
        for mesh in self.reductor.meshes:
            shaft_gear1 = mesh.gear1.shaft
            shaft_gear2 = mesh.gear2.shaft

            center_distance = ((shaft_gear1.pos_x - shaft_gear2.pos_x) ** 2 + (
                    shaft_gear1.pos_y - shaft_gear2.pos_y) ** 2) ** (1 / 2)
            # if center_distance != (mesh.gear1.diameter+mesh.gear2.diameter)/2:
            #     functional+=((center_distance-(mesh.gear1.diameter+mesh.gear2.diameter)/2)*100)**2
            # if center_distance==0:
            #     functional+=1000

            if mesh.gear2.diameter < mesh.gear2.shaft.diameter:
                functional += 10

            # if shaft_gear2.pos_x < shaft_gear1.pos_x:
            #     functional += 10

            # if shaft_gear2.pos_y < shaft_gear1.pos_y:
            #     functional += 10

            # if previous_radius_gear_1:

            #     if mesh.gear1.diameter/2 > previous_radius_gear_1+previous_radius_gear_2-previus_radius_shaft:
            #         functional += 10

            #     if (mesh.gear1.diameter+mesh.gear2.diameter-shaft_gear2.diameter)/2 < previous_radius_gear_2:
            #         functional += 10

            for gear in [mesh.gear1, mesh.gear2]:
                if gear.module == 0:
                    functional += 1000

                if gear.shaft.pos_x - gear.diameter / 2 < self.x_min_max[0]:
                    functional += (gear.shaft.pos_x - gear.diameter / 2 - self.x_min_max[0]) ** 2

                if gear.shaft.pos_x + gear.diameter / 2 > self.x_min_max[1]:
                    functional += (gear.shaft.pos_x - gear.diameter / 2 - self.x_min_max[1]) ** 2

                if gear.shaft.pos_y - gear.diameter / 2 < self.y_min_max[0]:
                    functional += (gear.shaft.pos_y - gear.diameter / 2 - self.y_min_max[0]) ** 2

                if gear.shaft.pos_y + gear.diameter / 2 > self.y_min_max[1]:

                    functional += (gear.shaft.pos_y - gear.diameter / 2 - self.y_min_max[1]) ** 2

            previous_radius_gear_1 = mesh.gear1.diameter / 2
            previous_radius_gear_2 = mesh.gear2.diameter / 2
            previus_radius_shaft = shaft_gear1.diameter / 2

        functional += self.reductor.mass() / 10

        return functional

    def cond_init(self):
        x0 = []
        for interval in self.bounds:
            x0.append((interval[1] - interval[0]) * float(npy.random.random(1)) + interval[0])
        return x0

    def optimize(self, max_loops: int = 1000):
        valid = True
        count = 0

        while valid and count < max_loops:
            x0 = self.cond_init()
            self.reductor.update(x0)
            res = minimize(self.objective, x0, bounds=self.bounds)
            count += 1
            if res.fun < 10 and res.success:
                print(count)
                self.reductor.update(res.x)

                return self.reductor

        return self.reductor


class Generator(DessiaObject):

    def __init__(self, motor: Motor, speed_output: float, precision: float = 0.1, z_min_max: Tuple[int, int] = [4, 80],
                 length_gears: float = 0.01, name: str = ''):
        self.motor = motor
        self.speed_output = speed_output
        self.length_gears = length_gears
        self.z_min_max = z_min_max
        self.precision = precision
        self.speed_input = motor.speed
        DessiaObject.__init__(self, name=name)

    def instanciate(self):
        shafts = [Shaft(pos_x=0, pos_y=0, length=0.1), Shaft(pos_x=0, pos_y=0, length=0.1),
                  Shaft(pos_x=0, pos_y=0, length=0.1)]

        gear1 = Gear(z=1, length=self.length_gears, shaft=shafts[0])
        gear2 = Gear(z=1, length=self.length_gears, shaft=shafts[1])
        gear3 = Gear(z=1, length=self.length_gears, shaft=shafts[1])
        gear4 = Gear(z=1, length=self.length_gears, shaft=shafts[2])
        meshes = [Mesh(gear1, gear2), Mesh(gear3, gear4)]

        reductor = Reductor(self.motor, shafts, meshes)
        return reductor

    def generate(self):
        list_node = []
        list_gear = []
        reductor = self.instanciate()

        for meshe in reductor.meshes:
            for gear in [meshe.gear1, meshe.gear2]:
                list_node.append(self.z_min_max[1] - self.z_min_max[0])
                list_gear.append(gear)
        tree = dt.RegularDecisionTree(list_node)
        list_reductor = []

        while not tree.finished:
            valid = True
            node = tree.current_node
            list_gear[len(node) - 1].z = node[-1] + self.z_min_max[0]
            if len(node) == 2 or len(node) == 4:
                if self.speed_input < self.speed_output:
                    if node[-2] <= node[-1]:
                        valid = False
                else:
                    if node[-2] >= node[-1]:
                        valid = False

                if math.gcd(list_gear[len(node) - 1].z, list_gear[len(node) - 2].z) != 1:
                    valid = False

            if len(node) == len(list_gear) and valid:
                if self.speed_output * (1 - self.precision) < reductor.speed_output() < self.speed_output * (1 + self.precision):
                    list_reductor.append(copy.deepcopy(reductor))
                else:
                    valid = False

            tree.NextNode(valid)

        return list_reductor
