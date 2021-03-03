import volmdlr as vm
import volmdlr.primitives2d as p2d
import volmdlr.primitives3d as p3d
import plot_data.core as plot_data
import math
from itertools import product

from dessia_common import DessiaObject
from typing import List
from plot_data.colors import *


class Panel(DessiaObject):
    _standalone_in_db = True

    def __init__(self, length: float, height: float,
                 thickness: float, mass: float = None,
                 name: str = ''):
        self.thickness = thickness
        self.height = height
        self.length = length
        self.mass = 7800*(thickness*height*length)
        DessiaObject.__init__(self, name=name)

    def contour(self):
        p0 = vm.Point2D(-self.length / 2, -self.height / 2)
        p1 = vm.Point2D(-self.length / 2, self.height / 2)
        p2 = vm.Point2D(self.length / 2, self.height / 2)
        p3 = vm.Point2D(self.length / 2, -self.height / 2)
        b1 = p2d.ClosedRoundedLineSegments2D([p0, p1, p2, p3], {})
        return vm.wires.Contour2D(b1.primitives)

    def volmdlr_primitives(self, center=vm.O3D, dir1=vm.X3D, dir2=vm.Y3D):
        contour = self.contour()
        dir3 = dir1.cross(dir2)
        profile = p3d.ExtrudedProfile(center, dir1, dir2, contour, [], self.thickness * dir3,
                                      name='extrusion')
        return [profile]

    def plot_data(self):
        hatching = plot_data.HatchingSet(0.1)
        edge_style = plot_data.EdgeStyle(line_width=1)
        surface_style = plot_data.SurfaceStyle(hatching=hatching)
        contour = self.contour()
        plot_datas = contour.plot_data(edge_style=edge_style, surface_style=surface_style)
        return [plot_data.PrimitiveGroup(primitives=[plot_datas])]


class PanelCombination(DessiaObject):
    _standalone_in_db = True

    def __init__(self, panels: List[Panel], grids: List[vm.Point3D], mass:float=None,
                 name: str = ''):
        self.grids = grids
        self.panels = panels
        self.mass = sum([p.mass for p in panels])
        DessiaObject.__init__(self, name=name)

    def plot_data(self):
        plot_datas = []
        hatching = plot_data.HatchingSet(0.1)
        edge_style = plot_data.EdgeStyle(line_width=1)
        surface_style = plot_data.SurfaceStyle(hatching=hatching)

        for panel, grid in zip(self.panels, self.grids):
            c = panel.contour()
            contour = c.translation(grid, copy=True)
            plot_datas.append(contour.plot_data(edge_style=edge_style, surface_style=surface_style))
        contour_inter = self.intersection_area()
        plot_datas.append(contour_inter.plot_data(edge_style=edge_style, surface_style=plot_data.SurfaceStyle()))
        return plot_datas

    def intersection_area(self):
        c1 = self.panels[0].contour()
        c2 = self.panels[1].contour()
        c2 = c2.translation(self.grids[1], copy=True)
        sol = c1.cut_by_linesegments(c2.primitives)
        return sol


class Rivet(DessiaObject):
    _standalone_in_db = True

    def __init__(self, rivet_diameter: float, rivet_length: float,
                 head_diameter: float, head_length: float, mass: float = None,
                 name: str = ''):
        self.head_diameter = head_diameter
        self.head_length = head_length
        self.rivet_diameter = rivet_diameter
        self.rivet_length = rivet_length
        self.mass = 7800*(math.pi*(head_diameter**2)/4*head_length + math.pi*(rivet_diameter**2)/4*rivet_length)

        DessiaObject.__init__(self, name=name)

    def contour(self, full_contour=False):

        p0 = vm.Point2D(0, 0)
        vectors = [vm.Vector2D(self.rivet_diameter / 2, 0),
                   vm.Vector2D(self.head_diameter / 2 - self.rivet_diameter / 2, 0),
                   vm.Vector2D(0, self.head_length),
                   vm.Vector2D(-self.head_diameter, 0),
                   vm.Vector2D(0, -self.head_length),
                   vm.Vector2D(self.head_diameter / 2 - self.rivet_diameter / 2, 0),
                   vm.Vector2D(0, -self.rivet_length),
                   vm.Vector2D(self.rivet_diameter, 0),
                   vm.Vector2D(0, self.rivet_length),
                   ]
        points = []
        p_init = p0
        for v in vectors:
            p1 = p_init.translation(v, copy=True)
            points.append(p1)
            p_init = p1

        c = p2d.ClosedRoundedLineSegments2D(points, {})
        if full_contour:
            return vm.wires.Contour2D(c.primitives)
        else:
            line = vm.edges.Line2D(p0, p0.translation(vm.Vector2D(0, -self.rivet_length), copy=True))
            contour = vm.wires.Contour2D(c.primitives)
            return contour.cut_by_line(line)[0]

    def volmdlr_primitives(self, center=vm.O3D, axis=vm.Z3D):
        contour = self.contour(full_contour=False)
        axis.normalize()
        y = axis.random_unit_normal_vector()
        z = axis.cross(y)
        irc = p3d.RevolvedProfile(center, z, axis, contour, center,
                                  axis, angle=2 * math.pi, name='Rivet')
        return [irc]

    def plot_data(self, full_contour=True):
        hatching = plot_data.HatchingSet(0.1)
        edge_style = plot_data.EdgeStyle(line_width=1)
        surface_style = plot_data.SurfaceStyle(hatching=hatching)
        contour = self.contour(full_contour=full_contour)
        plot_datas = contour.plot_data(edge_style=edge_style, surface_style=surface_style)
        return [plot_data.PrimitiveGroup(primitives=[plot_datas])]


class Rule(DessiaObject):
    _standalone_in_db = True

    def __init__(self, minimum_ratio: float,
                 maximum_ratio: float, name: str = ''):
        self.minimum_ratio = minimum_ratio
        self.maximum_ratio = maximum_ratio
        DessiaObject.__init__(self, name=name)

    def define_number_rivet(self, contour: vm.wires.Contour2D, rivet: Rivet):
        xmin, xmax, ymin, ymax = contour.bounding_rectangle()
        dir1 = xmax - xmin
        dir2 = ymax - ymin
        diameter = rivet.rivet_diameter
        max_distance_between_rivet = diameter / self.minimum_ratio
        min_distance_between_rivet = diameter / self.maximum_ratio
        number1_max = int(dir1 / min_distance_between_rivet)
        number1_min = max(1, int(dir1 / max_distance_between_rivet))
        number2_max = int(dir2 / min_distance_between_rivet)
        number2_min = max(1, int(dir2 / max_distance_between_rivet))

        if number1_max == 0 or number2_max == 0:
            return False
        numbers_in_dir1 = []
        for i in range(number1_max - number1_min + 1):
            numbers_in_dir1.append(number1_min + i)
        numbers_in_dir2 = []
        for i in range(number2_max - number2_min + 1):
            numbers_in_dir2.append(number2_min + i)

        all_possibilities = []
        for n1, n2 in product(numbers_in_dir1, numbers_in_dir2):
            all_possibilities.append([n1, n2])
        return all_possibilities


class PanelAssembly(DessiaObject):
    _standalone_in_db = True

    def __init__(self, panel_combination: PanelCombination,
                 rivet: Rivet, grids: List[vm.Point3D],
                 number_rivet1: int, number_rivet2: int,
                 number_rivet: int = None,
                 mass: float = None,
                 name: str = ''):
        self.number_rivet2 = number_rivet2
        self.number_rivet1 = number_rivet1
        self.number_rivet = number_rivet1*number_rivet2
        self.mass = rivet.mass * self.number_rivet + panel_combination.mass
        self.panel_combination = panel_combination
        self.rivet = rivet
        self.grids = grids
        DessiaObject.__init__(self, name=name)

    def contour(self):
        diameter = self.rivet.rivet_diameter
        circles = []
        for grid in self.grids:
            circles.append(vm.wires.Circle2D(grid, diameter))
        return circles

    def plot_data(self):
        edge_style = plot_data.EdgeStyle(line_width=1, color_stroke=RED)
        plot_datas = self.panel_combination.plot_data()
        circles = self.contour()
        plot_datas.extend([c.plot_data(edge_style=edge_style) for c in circles])
        return [plot_data.PrimitiveGroup(primitives=plot_datas)]


class Generator(DessiaObject):
    _standalone_in_db = True
    _dessia_methods = ['generate']

    def __init__(self, panel_combination: PanelCombination,
                 rivet: Rivet, rule: Rule, name: str = ''):
        self.rule = rule
        self.panel_combination = panel_combination
        self.rivet = rivet
        DessiaObject.__init__(self, name=name)

    def define_grid(self, contour: vm.wires.Contour2D, number_rivet1: int, number_rivet2: int):
        xmin, xmax, ymin, ymax = contour.bounding_rectangle()
        dir1 = xmax - xmin
        dir2 = ymax - ymin
        ratio1 = dir1 / (number_rivet1 + 1)
        ratio2 = dir2 / (number_rivet2 + 1)

        grids = []
        for n1 in range(number_rivet1):
            for n2 in range(number_rivet2):
                grids.append(vm.Point2D(xmin + ratio1 * (n1 + 1), ymin + ratio2 * (n2 + 1)))
        return grids

    def generate(self)->List[PanelAssembly]:
        contour = self.panel_combination.intersection_area()
        all_possibilities = self.rule.define_number_rivet(contour, self.rivet)
        solutions = []
        if all_possibilities is not False:
            for p in all_possibilities:
                grids = self.define_grid(contour, p[0], p[1])
                solutions.append(PanelAssembly(self.panel_combination, self.rivet, grids, p[0], p[1]))
        return solutions
