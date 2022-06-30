import volmdlr as vm
import volmdlr.primitives2d as p2d
import volmdlr.primitives3d as p3d
import plot_data.core as plot_data
import math
from itertools import product

from dessia_common import DessiaObject, PhysicalObject
from typing import List, Tuple, Dict
from plot_data.colors import *

class Color(DessiaObject):
    _standalone_in_db = False

    def __init__(self, red: float,
                 green: float, blue: float, name: str = ''):
        self.red = red
        self.green = green
        self.blue = blue
        DessiaObject.__init__(self, name=name)

    def to_tuple(self):
        return (self.red, self.green, self.blue)

class Panel(PhysicalObject):
    """ 
    :param length: A value corresponding to the panel length.
    :type length: float
    :param height: A value corresponding to the panel height.
    :type height: float
    :param thickness: A value corresponding to the panel thickness.
    :type thickness: float
    :param name: The name of the Panel.
    :type name: str
    """
    _standalone_in_db = True

    def __init__(self, length: float, height: float,
                 thickness: float, mass: float = None,
                 color: Color = Color(0, 0, 1), alpha: float = 0.3, name: str = ''):
        self.thickness = thickness
        self.height = height
        self.length = length
        self.mass = 7800 * (thickness * height * length)  # If you want to change the volumic mass, change the '7800'.
        self.color = color
        self.alpha = alpha
        PhysicalObject.__init__(self, name=name)

    def contour(self):
        p0 = vm.Point2D(-self.length / 2, -self.height / 2)
        p1 = vm.Point2D(-self.length / 2, self.height / 2)
        p2 = vm.Point2D(self.length / 2, self.height / 2)
        p3 = vm.Point2D(self.length / 2, -self.height / 2)
        b1 = p2d.ClosedRoundedLineSegments2D([p0, p1, p2, p3], {})
        return vm.wires.Contour2D(b1.primitives)

    def hole(self, rivet_panel_position: List[vm.Point2D], diameter):
        circles = []
        for pos in rivet_panel_position:
            circles.append(vm.wires.Circle2D(pos, diameter / 2))
        return circles

    def volmdlr_primitives(self, center=vm.O3D, dir1=vm.X3D, dir2=vm.Y3D):
        if self.color is None:
            color = (0, 0, 1)
        else:
            color = self.color.to_tuple()
        contour = self.contour()
        dir3 = dir1.cross(dir2)
        profile = p3d.ExtrudedProfile(center, dir1, dir2, contour, [], self.thickness * dir3,
                                      name='extrusion', color=color, alpha=self.alpha)
        return [profile]

    def plot_data(self):
        hatching = plot_data.HatchingSet(0.1)
        edge_style = plot_data.EdgeStyle(line_width=1)
        surface_style = plot_data.SurfaceStyle(hatching=hatching)
        contour = self.contour()
        plot_datas = contour.plot_data(edge_style=edge_style, surface_style=surface_style)
        return [plot_data.PrimitiveGroup(primitives=[plot_datas])]


class PanelCombination(PhysicalObject):
    """ 
    :param panels: List of Panel representing a combination of panels.
    :type panels: List[Panel]
    :param grids: List of Point3D created with volmdlr representing each panel position.
    :type grids: List[vm.Point3D]
    :param name: The name of the PanelCombination.
    :type name: str
    """
    _standalone_in_db = True

    def __init__(self, panels: List[Panel], grids: List[vm.Point3D], mass: float = None,
                 name: str = ''):
        self.grids = grids
        self.panels = panels
        self.mass = sum([p.mass for p in panels])
        PhysicalObject.__init__(self, name=name)

    def plot_data(self):
        plot_datas = []
        hatching = plot_data.HatchingSet(0.1)
        edge_style = plot_data.EdgeStyle(line_width=1)
        surface_style = plot_data.SurfaceStyle(hatching=hatching)

        for panel, grid in zip(self.panels, self.grids):
            c = panel.contour()
            contour = c.translation(grid)
            plot_datas.append(contour.plot_data(edge_style=edge_style, surface_style=surface_style))
        contour_inter = self.intersection_area()
        plot_datas.append(contour_inter.plot_data(edge_style=edge_style, surface_style=plot_data.SurfaceStyle()))
        return plot_datas

    def intersection_area(self):
        c1 = self.panels[0].contour()
        c2 = self.panels[1].contour()
        c2 = c2.translation(self.grids[1])
        sol = c1.cut_by_linesegments(c2.primitives)
        return sol

    def hole(self, rivet_position: List[vm.Point2D], diameter):
        dir1, dir2 = vm.X3D, vm.Y3D
        holes = []
        for panel, grid in zip(self.panels, self.grids):
            c2d = grid.plane_projection2d(vm.O3D, dir1, dir2)
            rivet_panel_position = [c - c2d for c in rivet_position]
            holes.append(panel.hole(rivet_panel_position, diameter))

        return holes

    def volmdlr_primitives(self):
        primitives = []
        for pan, pt3d in zip(self.panels, self.grids):
            primitives.extend(pan.volmdlr_primitives(center=pt3d))
        return primitives


class Rivet(PhysicalObject):
    """ 
    :param rivet_diameter: A value corresponding to the rivet body diameter.
    :type rivet_diameter: float
    :param rivet_length: A value corresponding to the rivet body length.
    :type rivet_length: float
    :param head_diameter: A value corresponding to the rivet head diameter.
    :type head_diameter: float
    :param head_length: A value corresponding to the rivet head length.
    :type head_length: float
    :param name: The name of the Rivet.
    :type name: str
    """
    _standalone_in_db = True

    def __init__(self, rivet_diameter: float, rivet_length: float,
                 head_diameter: float, head_length: float, mass: float = None,
                 name: str = ''):
        self.head_diameter = head_diameter
        self.head_length = head_length
        self.rivet_diameter = rivet_diameter
        self.rivet_length = rivet_length
        self.mass = 7800 * (math.pi * (head_diameter ** 2) / 4 * head_length + math.pi * (
                rivet_diameter ** 2) / 4 * rivet_length)

        PhysicalObject.__init__(self, name=name)

    def contour(self, full_contour=False):

        if full_contour:
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
        else:
            p0 = vm.Point2D(0, 0)
            vectors = [vm.Vector2D(0, self.rivet_diameter / 2),
                       vm.Vector2D(0, self.head_diameter / 2 - self.rivet_diameter / 2),
                       vm.Vector2D(self.head_length, 0),
                       vm.Vector2D(0, -self.head_diameter / 2),
                       vm.Vector2D(-self.head_length - self.rivet_length, 0),
                       vm.Vector2D(0, self.rivet_diameter / 2),
                       vm.Vector2D(self.rivet_length, 0),
                       ]

        points = []
        p_init = p0
        for v in vectors:
            p1 = p_init.translation(v)
            points.append(p1)
            p_init = p1
        return vm.wires.ClosedPolygon2D(points)

    def volmdlr_primitives(self, center=vm.O3D, axis=vm.Z3D):
        contour = self.contour(full_contour=False)
        axis.normalize()
        y = axis.random_unit_normal_vector()
        z = axis.cross(y)
        irc = p3d.RevolvedProfile(center, axis, z, contour, center,
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
    """ 
    :param minimum_ratio: A value corresponding to a ratio between rivet body diameter \
    and the maximal distance with another rivet.
    :type minimum_ratio: float
    :param maximum_ratio: A value corresponding to a ratio between rivet body diameter \
    and the minimal distance with another rivet.
    :type maximum_ratio: float
    :param name: The name of the Rule.
    :type name: str
    """
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


class PanelAssembly(PhysicalObject):
    """ 
    :param panel_combination: The PanelCombination used as work base.
    :type panel_combination: PanelCombination
    :param rivet: The rivet used as work base.
    :type rivet: Rivet
    :param grids: List of Point2D created with volmdlr representing each rivet position\
    in panel_combination intersection surface.
    :type grids: List[vm.Point2D]
    :param number_rivet1: An integer corresponding to the number of rivet in x direction.
    :type number_rivet1: int
    :param number_rivet2: An integer corresponding to the number of rivet in y direction.
    :type number_rivet2: int
    :param name: The name of the PanelAssembly.
    :type name: str
    """
    _standalone_in_db = True

    def __init__(self, panel_combination: PanelCombination,
                 rivet: Rivet, grids: List[vm.Point2D],
                 number_rivet1: int, number_rivet2: int,
                 name: str = ''):

        self.number_rivet2 = number_rivet2
        self.number_rivet1 = number_rivet1
        self.panel_combination = panel_combination
        self.rivet = rivet
        self.grids = grids
        PhysicalObject.__init__(self, name=name)

        self.number_rivet = number_rivet1 * number_rivet2
        self.mass = rivet.mass * self.number_rivet + panel_combination.mass
        self.pressure_applied = self._pressure_applied()
        self.fatigue_resistance = self._fatigue_resistance()

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

    def _pressure_applied(self):
        force_applied = 100  # Newton
        surface_rivet = (math.pi * self.rivet.head_diameter ** 2) / 4
        pressure_applied = force_applied / (self.number_rivet * surface_rivet)
        return pressure_applied

    def _fatigue_resistance(self):
        number_hour_worked = 5000  # hours
        test_rivet = 5  # Newton
        surface_rivet = (math.pi * self.rivet.head_diameter ** 2) / 4
        pressure_test = test_rivet / surface_rivet

        distance_between_riv = []
        for n, pos in enumerate(self.grids):
            if n == len(self.grids) - 1:
                distance_between_riv.append((pos - self.grids[0]).norm())
            else:
                distance_between_riv.append((pos - self.grids[n + 1]).norm())
        ratio_distance = min(distance_between_riv) / (4.5 * self.rivet.head_diameter)
        coeff_security = 3
        ratio_pressure = (pressure_test / self.pressure_applied) / coeff_security
        fatigue = number_hour_worked * ratio_distance * ratio_pressure
        return fatigue

    def volmdlr_primitives(self):
        pan_vm = self.panel_combination.volmdlr_primitives()
        primitives = pan_vm
        center, dir1, dir2 = pan_vm[0].plane_origin, pan_vm[0].x, pan_vm[0].y
        # holes = self.panel_combination.hole(self.grids, self.rivet.rivet_diameter)
        thickness = vm.O3D + 2*pan_vm[0].extrusion_vector
        # for panel, pan_vm, hole in zip(self.panel_combination.panels, self.panel_combination.volmdlr_primitives(),
        #                                holes):
        #     center, dir1, dir2 = pan_vm.plane_origin, pan_vm.x, pan_vm.y
        #     contour, dir3 = panel.contour(), pan_vm.extrusion_vector
        #     thickness += dir3
        #
        #     pan_hole = p3d.ExtrudedProfile(center, dir1, dir2, contour, [], dir3,
        #                                    name='extrusion')
        #     primitives.append(pan_hole)

        for grid in self.grids:
            pos_riv = dir1 * grid[0] + dir2 * grid[1] + thickness
            primitives.extend(self.rivet.volmdlr_primitives(center=pos_riv))

        return primitives


class Generator(DessiaObject):
    """ 
    :param panel_combination: The PanelCombination used as work base.
    :type panel_combination: PanelCombination
    :param rivet: The rivet used as work base.
    :type rivet: Rivet
    :param rule: The rule used as work base.
    :type rule: Rule
    :param name: The name of the Generator.
    :type name: str
    """
    _standalone_in_db = True
    _dessia_methods = ['generate']

    def __init__(self, panel_combination: PanelCombination,
                 rivet: Rivet, rule: Rule, name: str = ''):
        self.rule = rule
        self.panel_combination = panel_combination
        self.rivet = rivet
        DessiaObject.__init__(self, name=name

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

    def generate(self) -> List[PanelAssembly]:
        contour = self.panel_combination.intersection_area()
        all_possibilities = self.rule.define_number_rivet(contour, self.rivet)
        solutions = []
        if all_possibilities is not False:
            for p in all_possibilities:
                grids = self.define_grid(contour, p[0], p[1])
                solutions.append(PanelAssembly(self.panel_combination, self.rivet, grids, p[0], p[1]))
        return solutions
