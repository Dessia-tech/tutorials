import math
from itertools import product
from random import random
from typing import List

import cma
import plot_data.core as plot_data
import volmdlr as vm
import volmdlr.primitives2d as p2d
import volmdlr.primitives3d as p3d
from dessia_common.core import DessiaObject


class Component(DessiaObject):
    _standalone_in_db = True

    def __init__(self, p0: vm.Point2D, p1: vm.Point2D, p2: vm.Point2D, p3: vm.Point2D, name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.p3 = p3
        self.p2 = p2
        self.p1 = p1
        self.p0 = p0
        self.primitive = self._primitive()

    def _primitive(self):
        points = [self.p0, self.p1, self.p2, self.p3]
        l1 = vm.primitives2d.ClosedRoundedLineSegments2D(points, {})
        return l1

    def update(self, p0: vm.Point2D, p1: vm.Point2D, p2: vm.Point2D, p3: vm.Point2D):
        self.p3 = p3
        self.p2 = p2
        self.p1 = p1
        self.p0 = p0

    def length(self):
        points = [self.p0, self.p1, self.p2, self.p3]
        length = 0
        for p1, p2 in zip(points[0:-1], points[1:]):
            length += p1.point_distance(p2)
        length += points[0].point_distance(points[-1])
        return length


class Optimizer(DessiaObject):
    _standalone_in_db = True
    _dessia_methods = ['optimize']

    def __init__(self, component: Component, name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.component = component

    def optimize(self) -> List[Component]:
        solutions = []
        for i in range(10):
            x0a = [random() for i in range(8)]

            xra, fx = cma.fmin(self.objective, x0a, 0.1,
                               options={'bounds': [0, 1],
                                        'tolfun': 1e-8,
                                        'verbose': 10,
                                        'ftarget': 1e-8,
                                        'maxiter': 100})[0:2]

            x_sol = xra
            points = [vm.Point2D(x_sol[2 * i], x_sol[2 * i + 1]) for i in range(int(len(x_sol) / 2.))]
            self.component.update(*points)
            length = self.component.length()
            if abs(length - 0.2) < 1e-3:
                solutions.append(self.component.copy())
        return solutions

    def objective(self, x):
        objective = 0
        points = [vm.Point2D(x[2 * i], x[2 * i + 1]) for i in range(int(len(x) / 2.))]
        self.component.update(*points)
        length = self.component.length()
        length_obj = 0.2
        return (length - length_obj)**2
