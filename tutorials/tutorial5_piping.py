import volmdlr as vm
import volmdlr.primitives2d as p2d
import volmdlr.primitives3d as p3d
import plot_data.core as plot_data
import math
from itertools import product

from dessia_common import DessiaObject
from typing import List


class Housing(DessiaObject):
    _standalone_in_db = True

    def __init__(self, faces: List[vm.faces.Face3D], origin: vm.Point3D,
                 name: str = ''):
        self.origin = origin
        self.faces = faces
        DessiaObject.__init__(self, name=name)

    def volmdlr_primitives(self):
        for face in self.faces:
            face.translation(self.origin, copy=False)
        return self.faces

class Frame(DessiaObject):
    _standalone_in_db = True

    def __init__(self, start: vm.Point3D, end: vm.Point3D,
                 name: str = ''):
        self.start = start
        self.end = end
        self.line = vm.edges.LineSegment3D(start, end)
        DessiaObject.__init__(self, name=name)

    def define_waypoints(self, abs_curvs=List[float]):
        points = []
        for abs_curv in abs_curvs:
            points.append(self.line.point_at_abscissa(abs_curv))
        return points

class Piping(DessiaObject):
    _standalone_in_db = True

    def __init__(self, start: vm.Point3D, end: vm.Point3D, diameter: float,
                 minimum_radius: float, name: str = ''):
        self.minimum_radius = minimum_radius
        self.diameter = diameter
        self.start = start
        self.end = end
        DessiaObject.__init__(self, name=name)

    def update_waypoints(self, new_points : List[vm.Point3D]):
        return [self.start] + new_points + [self.end]

    def route(self, points: List[vm.Point3D]):
        lines = []
        for p1, p2 in zip(points[0:-1], points[1:]):
            lines.append(vm.edges.LineSegment3D(p1, p2))
        return lines

    def generate_sweep(self, points:List[vm.Point3D]):
        c = vm.wires.Circle2D(vm.Point2D(0, 0), self.diameter / 2)
        radius = {i:self.minimum_radius for i in [j + 1 for j in range(len(points)-2)]}
        rl = p3d.OpenRoundedLineSegments3D(points, radius, adapt_radius=True, name='wire')
        contour = vm.wires.Contour2D([c])
        sweep = p3d.Sweep(contour, rl, color='black', name='piping')
        return [sweep]


class Assembly(DessiaObject):
    _standalone_in_db = True

    def __init__(self, frame: Frame, piping: Piping, housing: Housing,
                 name: str = ''):

        DessiaObject.__init__(self, name=name)
        self.housing = housing
        self.piping = piping
        self.frame = frame

        self.waypoints = self.update_waypoints([0.4, 0.6])
        self.routes = self.update_route(self.waypoints)

    def update_waypoints(self, pourcentages: List[float]):

        length = self.frame.line.length()
        abs_points = []
        for pourcentage in pourcentages:
            abs_points.append(pourcentage*length)
        points = self.frame.define_waypoints(abs_points)
        return self.piping.update_waypoints(points)

    def update_route(self, points:List[vm.Point3D]):
        return self.piping.route(points)

    def volmdlr_primitives(self):
        primitives = self.piping.generate_sweep(self.waypoints)
        primitives.extend(self.housing.volmdlr_primitives())
        return primitives