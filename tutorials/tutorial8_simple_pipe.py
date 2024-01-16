import volmdlr as vm
import volmdlr.primitives2d as p2d
import volmdlr.primitives3d as p3d
import plot_data.core as plot_data
import math
from itertools import product
from random import random
import cma
import networkx as nx

from dessia_common.core import DessiaObject, PhysicalObject
from typing import List


class Housing(DessiaObject):
    _standalone_in_db = False

    def __init__(self, faces: List[vm.faces.Face3D], origin: vm.Point3D,
                 name: str = ''):
        self.origin = origin
        self.faces = faces
        DessiaObject.__init__(self, name=name)

    def volmdlr_primitives(self):
        for face in self.faces:
            face.translation(self.origin)
        return self.faces


class Frame(DessiaObject):
    _standalone_in_db = False

    def __init__(self, start: vm.Point3D, end: vm.Point3D,
                 position: vm.Point3D = None,
                 name: str = ''):
        self.position = position
        self.start = start
        self.end = end
        self.line = vm.edges.LineSegment3D(start, end)
        DessiaObject.__init__(self, name=name)

    def define_waypoint(self, pourcentage_abs_curv=float):
        length = self.line.length()
        self.position = self.line.point_at_abscissa(pourcentage_abs_curv * length)
        return self.position


class Piping(DessiaObject):
    _standalone_in_db = True

    def __init__(self, diameter: float, length_connector: float,
                 minimum_radius: float, routes: List[vm.edges.LineSegment3D] = None,
                 name: str = ''):
        self.routes = routes
        self.length_connector = length_connector
        self.minimum_radius = minimum_radius
        self.diameter = diameter
        DessiaObject.__init__(self, name=name)

    def route(self, points: List[vm.Point3D]):
        lines = []
        for p1, p2 in zip(points[0:-1], points[1:]):
            lines.append(vm.edges.LineSegment3D(p1, p2))
        return lines

    def length(self):
        length = 0
        for line in self.routes:
            length += line.length()
        return length

    def genere_neutral_fiber(self, points: List[vm.Point3D]):
        radius = {i: self.minimum_radius for i in [j + 1 for j in range(len(points) - 2)]}
        rl = p3d.OpenRoundedLineSegments3D(points, radius, adapt_radius=True, name='wire')
        return rl

    def generate_sweep(self, color=(248 / 255, 205 / 255, 70 / 255), alpha=0.8):
        circle = vm.curves.Circle2D(vm.Point2D(0, 0), self.diameter / 2)
        contour = vm.wires.Contour2D(circle.split_at_abscissa(circle.length() * .5))
        points = []
        for l in self.routes:
            if l.start not in points:
                points.append(l.start)
            if l.end not in points:
                points.append(l.end)
        rl = self.genere_neutral_fiber(points)
        sweep = p3d.Sweep(contour, rl, color=color, alpha=alpha, name='piping')
        return [sweep]

    def define_waypoint(self, pourcentage_abs_curv: float):
        lines = self.routes
        total_length = sum([l.length() for l in lines])
        length = 0
        for l in lines:
            length += l.length()
            if pourcentage_abs_curv * total_length <= length:
                return l.point_at_abscissa(l.length() - (length - pourcentage_abs_curv * total_length))


class MasterPiping(Piping):
    _standalone_in_db = True

    def __init__(self, start: vm.Point3D, end: vm.Point3D,
                 direction_start: vm.Vector3D, direction_end: vm.Vector3D,
                 diameter: float, length_connector: float,
                 minimum_radius: float, routes: List[vm.edges.LineSegment3D] = None,
                 name: str = ''):
        self.direction_end = direction_end
        self.direction_start = direction_start
        self.start = start
        self.end = end
        Piping.__init__(self, diameter=diameter, length_connector=length_connector,
                        minimum_radius=minimum_radius, routes=routes, name=name)

    def update(self, new_point: vm.Point3D):
        direction_start = self.direction_start.copy()
        direction_start.normalize()
        pt_start_connector = self.start + self.length_connector * direction_start
        direction_end = self.direction_end.copy()
        direction_end.normalize()
        pt_end_connector = self.end + self.length_connector * direction_end
        points = [self.start, pt_start_connector] + [new_point] + [pt_end_connector, self.end]
        self.routes = self.route(points)


class SlavePiping(Piping):
    _standalone_in_db = True

    def __init__(self, start: vm.Point3D, direction_start: vm.Vector3D,
                 piping_master: Piping,
                 diameter: float, length_connector: float,
                 minimum_radius: float, routes: List[vm.edges.LineSegment3D] = None,
                 name: str = ''):
        self.piping_master = piping_master
        self.direction_start = direction_start
        self.start = start
        Piping.__init__(self, diameter=diameter, length_connector=length_connector,
                        minimum_radius=minimum_radius, routes=routes, name=name)

    def update(self, new_point: vm.Point3D):
        direction_start = self.direction_start.copy()
        direction_start.normalize()
        pt_start_connector = self.start + self.length_connector * direction_start
        points = [self.start, pt_start_connector, new_point]
        self.routes = self.route(points)


#
class Assembly(PhysicalObject):
    _standalone_in_db = True
    _non_data_eq_attributes = ['length', 'min_radius', 'max_radius', 'distance_input',
                               'straight_line', 'routes']

    def __init__(self, frame: Frame, pipings: List[Piping], housing: Housing,
                 waypoint: vm.Point3D = None, name: str = ''):

        PhysicalObject.__init__(self, name=name)
        self.housing = housing
        self.pipings = pipings
        self.frame = frame

        graph = self.graph()
        self.analyze_pipings = self.analyze_graph(graph)

    def graph(self):
        graph = nx.Graph()
        for piping in self.pipings:
            if isinstance(piping, SlavePiping):
                graph.add_edges_from([(piping, piping.piping_master)])
        return graph

    def analyze_graph(self, graph):
        if len(self.pipings) > 1:
            for n in graph.degree():
                if isinstance(n[0], MasterPiping) and n[1] == 1:
                    node_input = n[0]
            list_piping = [node_input]
            order_list = (list(nx.dfs_edges(graph, source=node_input)))
            for n1, n2 in order_list:
                if n2 not in list_piping:
                    list_piping.append(n2)
            return list_piping
        else:
            return self.pipings

    def update(self, pourcentages: List[float]):
        initial_point = self.frame.define_waypoint(pourcentages[0])
        self.analyze_pipings[0].update(initial_point)
        for indice_piping, (piping, pourcentage) in enumerate(zip(self.analyze_pipings[1:], pourcentages[1:])):
            point = self.analyze_pipings[indice_piping].define_waypoint(pourcentage)
            piping.update(point)

    def length(self):
        length = 0
        for piping in self.pipings:
            length += piping.length()
        return length

    def volmdlr_primitives(self):
        primitives = []
        for piping in self.analyze_pipings:
            primitives.extend(piping.generate_sweep())
        primitives.extend(self.housing.volmdlr_primitives())
        return primitives


class Optimizer(DessiaObject):
    _standalone_in_db = True
    _dessia_methods = ['optimize']

    def __init__(self, assembly: Assembly, objective_length: float, name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.objective_length = objective_length
        self.assembly = assembly

    def optimize(self):
        sol_opt = math.inf
        for i in range(100):
            x0a = [random() for i in range(len(self.assembly.pipings))]
            xra, fx = cma.fmin(self.objective, x0a, 0.1,
                               options={'bounds': [0, 1],
                                        'tolfun': 1e-8,
                                        'verbose': 10,
                                        'ftarget': 1e-8,
                                        'maxiter': 10})[0:2]
            self.assembly.update(xra)
            if self.assembly.length() < sol_opt:
                sol_opt = self.assembly.length()
                x_opt = xra
        self.assembly.update(x_opt)

    def objective(self, x):
        self.update(x)
        return (self.assembly.length() - self.objective_length) ** 2

    def update(self, x):
        self.assembly.update(x)
