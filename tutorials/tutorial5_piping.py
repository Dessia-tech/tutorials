from random import random
from typing import List

import cma
import volmdlr as vm
import volmdlr.faces
import volmdlr.primitives3d as p3d
from dessia_common.core import DessiaObject, PhysicalObject
from dessia_common.decorators import cad_view
from volmdlr.model import VolumeModel
from volmdlr.shapes import Solid


class Housing(PhysicalObject):
    _standalone_in_db = False

    def __init__(self, faces: List[vm.shapes.Shell], origin: vm.Point3D,
                 name: str = ''):
        self.origin = origin
        self.faces = faces
        PhysicalObject.__init__(self, name=name)

    def volmdlr_primitives(self):
        for face in self.faces:
            face.translation(self.origin)
        return self.faces

    @cad_view(selector='Housing CAD')
    def cad_view(self):
        primitives = self.volmdlr_primitives()
        return VolumeModel(primitives=primitives).babylon_data()


class Frame(DessiaObject):
    _standalone_in_db = False

    def __init__(self, start: vm.Point3D, end: vm.Point3D,
                 position: vm.Point3D = None, name: str = ''):
        self.position = position
        self.start = start
        self.end = end
        self.line = vm.edges.LineSegment3D(start, end)
        DessiaObject.__init__(self, name=name)

    def define_waypoints(self, pourcentage_abs_curv=float):
        length = self.line.length()
        abscissa = pourcentage_abs_curv * length
        self.position = self.line.point_at_abscissa(abscissa)
        return self.position


class Piping(DessiaObject):
    _standalone_in_db = True

    def __init__(self, start: vm.Point3D, end: vm.Point3D,
                 direction_start: vm.Vector3D, direction_end: vm.Vector3D,
                 diameter: float, length_connector: float,
                 minimum_radius: float, name: str = ''):
        self.length_connector = length_connector
        self.direction_end = direction_end
        self.direction_start = direction_start
        self.minimum_radius = minimum_radius
        self.diameter = diameter
        self.start = start
        self.end = end
        DessiaObject.__init__(self, name=name)

    def update_waypoints(self, new_points: List[vm.Point3D]):
        direction_start = self.direction_start.copy()
        direction_start.unit_vector()
        pt_start_connector = self.start + self.length_connector*direction_start
        direction_end = self.direction_end.copy()
        direction_end.unit_vector()
        pt_end_connector = self.end + self.length_connector * direction_end

        start_wpts = [self.start, pt_start_connector]
        end_wpts = [pt_end_connector, self.end]
        return start_wpts + new_points + end_wpts

    def route(self, points: List[vm.Point3D]):
        lines = []
        for p1, p2 in zip(points[0:-1], points[1:]):
            lines.append(vm.edges.LineSegment3D(p1, p2))
        return lines

    def length(self, routes):
        length = 0
        for line in routes:
            length += line.length()
        return length

    def genere_neutral_fiber(self, points: List[vm.Point3D]):
        point_indices = [j + 1 for j in range(len(points) - 2)]
        radius = {i: self.minimum_radius for i in point_indices}
        rl = p3d.OpenRoundedLineSegments3D(points, radius,
                                           adapt_radius=True, name='wire')
        return rl

    def generate_sweep(self, points: List[vm.Point3D],
                       color=(248/255, 205/255, 70/255), alpha=0.8):
        circle = vm.curves.Circle2D.from_center_and_radius(vm.Point2D(0, 0), self.diameter / 2)
        contour = vm.wires.Contour2D(circle.split_at_abscissa(circle.length() * .5))
        rl = self.genere_neutral_fiber(points)
        # contour = vm.wires.Contour2D([c])
        sweep = Solid.make_sweep_from_contour(section=contour, path=rl)
        return [sweep]


class Assembly(PhysicalObject):
    _standalone_in_db = True
    _non_data_eq_attributes = ['length', 'min_radius', 'max_radius',
                               'distance_input', 'straight_line', 'routes']

    def __init__(self, frames: List[Frame], piping: Piping, housing: Housing,
                 waypoints: List[vm.Point3D] = None, name: str = ''):

        PhysicalObject.__init__(self, name=name)
        self.housing = housing
        self.piping = piping
        self.frames = frames

        if waypoints is None:
            self.waypoints = self.update_waypoints([0.5] * len(self.frames))
        else:
            self.waypoints = waypoints
        self.routes = self.update_route(self.waypoints)

        rl = self.piping.genere_neutral_fiber(self.waypoints)
        self.length = self.piping.length(self.routes)
        radius = rl.radius
        min_radius = min(list(radius.values()))
        self.min_radius = min_radius
        max_radius = max(list(radius.values()))
        self.max_radius = max_radius
        self.distance_input = self.piping.start.point_distance(self.piping.end)
        length = 0
        for primitive in rl.primitives:
            if not isinstance(primitive, vm.edges.Arc3D):
                length += primitive.length()
        self.straight_line = length

    def update_waypoints(self, pourcentages: List[float]):
        abs_points = []
        for frame, pourcentage in zip(self.frames, pourcentages):
            abs_points.append(frame.define_waypoints(pourcentage))
        return self.piping.update_waypoints(abs_points)

    def update(self, x: List[float]):
        self.waypoints = self.update_waypoints(x)
        self.routes = self.update_route(self.waypoints)

    def update_route(self, points:List[vm.Point3D]):
        return self.piping.route(points)

    def volmdlr_primitives(self):
        primitives = self.piping.generate_sweep(self.waypoints)
        primitives.extend(self.housing.volmdlr_primitives())
        return primitives

    @cad_view(selector='Assembly CAD')
    def cad_view(self):
        primitives = self.volmdlr_primitives()
        return VolumeModel(primitives=primitives).babylon_data()


class Optimizer(DessiaObject):
    _standalone_in_db = True
    _dessia_methods = ['optimize']

    def __init__(self, name: str = ''):
        DessiaObject.__init__(self, name=name)

    def optimize(self, assemblies: List[Assembly],
                 number_solution_per_assembly: int) -> List[Assembly]:
        solutions = []
        for assembly in assemblies:
            self.assembly = assembly

            x0a = [random() for i in range(len(self.assembly.frames))]

            check = True
            compt = 0
            number_solution = 0
            while check:
                xra, fx = cma.fmin(self.objective, x0a, 0.1,
                                   options={'bounds': [0, 1],
                                            'tolfun': 1e-8,
                                            'verbose': 10,
                                            'ftarget': 1e-8,
                                            'maxiter': 100})[0:2]
                waypoints = self.assembly.waypoints
                radius = self.assembly.piping.genere_neutral_fiber(waypoints).radius
                min_radius = min(list(radius.values()))
                if min_radius >= 0.9*self.assembly.piping.minimum_radius and len(list(radius.keys())) == len(waypoints) - 2:
                    new_assembly = self.assembly.copy()
                    new_assembly.update(xra)
                    solutions.append(new_assembly)
                compt += 1
                number_solution += 1
                if compt == 20 or number_solution_per_assembly == number_solution:
                    break

        return solutions

    def objective(self, x):
        objective = 0
        self.update(x)

        waypoints = self.assembly.waypoints
        radius = self.assembly.piping.genere_neutral_fiber(waypoints).radius
        min_radius = min(list(radius.values()))
        if min_radius < self.assembly.piping.minimum_radius:
            objective += 10 + (min_radius - self.assembly.piping.minimum_radius)**2
        else:
            objective += 10 - 0.1*(min_radius - self.assembly.piping.minimum_radius)

        return objective

    def update(self, x):
        self.assembly.update(x)
