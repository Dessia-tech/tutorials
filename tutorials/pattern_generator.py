import math
from typing import List, Tuple

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import plot_data
import volmdlr
import volmdlr.edges as vme
import volmdlr.wires as vmw
from dessia_common.core import DessiaObject
from dessia_common.decorators import plot_data_view
from plot_data.colors import BLACK, CYAN


# from scipy.optimize import bisect


class Piece(DessiaObject):
    _standalone_in_db = False
    _eq_is_data_eq = True
    _non_serializable_attributes = []
    _non_eq_attributes = ['name']
    _non_hash_attributes = ['name']

    """Peace used in the pattern"""

    def __init__(self, position: volmdlr.Point2D,
                 diameter: float, name: str = ''):

        self.position = position
        self.diameter = diameter
        DessiaObject.__init__(self, name=name)

    def mirror(self, axis: volmdlr.Vector2D):
        """
        calculates the mirrored object to a given axis
        """
        if axis == volmdlr.X2D:
            new_x = self.position[0]
            new_y = -self.position[1]
        elif axis == volmdlr.Y2D:
            new_x = -self.position[0]
            new_y = self.position[1]
        else:
            raise NotImplementedError
        return Piece(volmdlr.Point2D(new_x, new_y), self.diameter)

    def plot(self, ax=None, color: str = ''):
        """plots a Piece using the matplotlib dependence"""
        if ax is None:
            _, ax = plt.subplots()
            ax.set_aspect('equal')
        rayon = self.diameter / 2.
        circle = patches.Circle((self.position.x, self.position.y),
                                rayon, color=color, fill=False)
        ax.add_patch(circle)

    @plot_data_view(selector="Circle2D")
    def plot_data(self, edge_style: plot_data.EdgeStyle = None,
                  surface_style: plot_data.SurfaceStyle = None):
        """
        Dessia plot_data method
        return a plotdata.Circle2D object
        """
        if edge_style is None:
            edge_style = plot_data.EdgeStyle(line_width=1, color_stroke=BLACK,
                                             dashline=[])
        if surface_style is None:
            surface_style = plot_data.SurfaceStyle(color_fill=CYAN)
        return plot_data.Circle2D(cx=self.position.x,
                                  cy=self.position.y,
                                  r=self.diameter / 2,
                                  edge_style=edge_style,
                                  surface_style=surface_style)


class Pattern(DessiaObject):
    _standalone_in_db = True
    _eq_is_data_eq = True
    _non_serializable_attributes = []
    _non_eq_attributes = ['name']
    _non_hash_attributes = ['name']
    """defines a pattern on an elipse format"""

    def __init__(self, minor_axis_size_in_mm: float,
                 excentricity: float = None,
                 clearence: float = None,
                 piece_diameter: float = None, name: str = ''):
        self.minor_axis_size_in_mm = minor_axis_size_in_mm
        self.excentricity = excentricity
        self.clearence = clearence
        self.piece_diameter = piece_diameter
        self._utd_pieces = False
        self._utd_major_axis = False
        self._utd_arclength = False

        DessiaObject.__init__(self, name=name)

    def _get_pieces(self):
        """Calculates Pattern pieces"""
        horizontal_pieces = self.get_minor_axis_pieces()
        orbital_pieces = self.get_orbital_pieces(self.piece_diameter)
        return horizontal_pieces + orbital_pieces

    @property
    def pieces(self):
        """
        Pattern pieces
        """
        if not self._utd_pieces:
            self._pieces = self._get_pieces()
            self._utd_pieces = True
        return self._pieces

    @property
    def major_axis(self):
        """Elipse's major axis"""
        if not self._utd_major_axis:
            self._major_axis = self._get_major_axis()
            self._utd_major_axis = True
        return self._major_axis

    def _get_elipse_circunference(self):
        """Calculates the elipse's circunference Using
        the Ramanujan's first approximation formula """
        arclength = math.pi * (
                3 * (self.major_axis / 2 +
                     self.minor_axis_size_in_mm / 2
                     ) * math.sqrt((3 * self.major_axis / 2 +
                                    self.minor_axis_size_in_mm / 2
                                    ) * (self.major_axis / 2 +
                                         3 * (
                                                 self.minor_axis_size_in_mm / 2))))
        return arclength

    @property
    def elipse_circunference(self):
        """Elipse's circunference"""
        if not self._utd_arclength:
            self._arclegth = self._get_elipse_circunference()
            self._utd_arclength = True
        return self._arclegth

    def minor_axis_pieces_number(self):
        """
        Calculares how many pieces should
        be placed in the minor axis of the elispe,
        already considering clearence, if there is any
        returns: number of pieces
        """
        pieces_number = int(self.minor_axis_size_in_mm / (self.piece_diameter +
                                                          self.clearence))
        # print('self.clearence:', self.clearence)
        self.clearence = self.minor_axis_size_in_mm / pieces_number - self.piece_diameter
        # print('self.clearence2:', self.clearence)
        return pieces_number

    def get_minor_axis_pieces(self):
        """Places Generates the pieces in the minor axis
        returns: number of pieces"""
        list_pieces = []
        # print('self.minor_axis_pieces_number():', self.minor_axis_pieces_number())
        x_position = -self.minor_axis_size_in_mm / 2
        for i_piece in range(0, self.minor_axis_pieces_number() + 1):
            if i_piece != 0:
                x_position += self.clearence / 2
                x_position += self.piece_diameter / 2
            list_pieces.append(Piece(volmdlr.Point2D(x_position, 0),
                                     self.piece_diameter))
            x_position += self.piece_diameter / 2 + self.clearence / 2
        # line_segement = vme.LineSegment2D(
        #     volmdlr.Point2D(-self.minor_axis_size_in_mm / 2, 0),
        #     volmdlr.Point2D(self.minor_axis_size_in_mm / 2, 0))
        # ax = line_segement.plot()
        # for piece in list_pieces:
        #     piece.plot(ax=ax, color='r')
        #     piece.position.plot(ax=ax, color='b')
        return list_pieces

    def _get_major_axis(self):
        """Calculates the major axis of the elipse"""
        semi_major_axis = (self.minor_axis_size_in_mm / 2) / math.sqrt(
            1 - self.excentricity ** 2)
        return 2 * semi_major_axis

    def orbital_pieces_number(self, piece_diameter):
        """
        Calculates how many pieces are to be placed in the orbital contour
        """
        contour_length = self.get_elipse_interpolation().length()
        return int(contour_length / (piece_diameter + self.clearence))

    def get_elipse_interpolation(self):
        """
        Calculates the interpolation of an elipse
        """
        point1 = volmdlr.Point2D(self.minor_axis_size_in_mm / 2,
                                 self.piece_diameter + self.clearence)
        point2 = volmdlr.Point2D(0, self.major_axis / 2)
        point3 = volmdlr.Point2D(-self.minor_axis_size_in_mm / 2,
                                 self.piece_diameter + self.clearence)
        bspline1 = vme.BSplineCurve2D.from_points_interpolation([point1, point2, point3], 2)
        edges = []
        points = bspline1.discretization_points(number_points=40)
        for i in range(0, len(points) - 1):
            edges.append(volmdlr.edges.LineSegment2D(points[i], points[i + 1]))
        contour2 = vmw.Contour2D(edges)
        return contour2

    def get_orbital_pieces(self, piece_diameter):
        """
        calculates pieces to be placed on the elipse curve
        """
        list_pieces = []
        contour = self.get_elipse_interpolation()
        piece_points = contour.discretization_points(angle_resolution=piece_diameter + self.clearence)
        for point in piece_points:
            list_pieces.append(Piece(point, piece_diameter))
        list_pieces += Pattern.get_mirrored_pieces(list_pieces,
                                                   volmdlr.X2D, )
        return list_pieces

    @staticmethod
    def get_mirrored_pieces(list_pieces: List[Piece], axis: volmdlr.Vector2D):
        """
        gets all pieces mirrored to a given axis
        """
        new_list_pieces = []
        for piece in list_pieces:
            new_list_pieces.append(piece.mirror(axis))
        return new_list_pieces

    def plot(self, ax=None):
        if ax is None:
            _, ax = plt.subplots()
            ax.set_aspect('equal')
        # minor_axis = vme.LineSegment2D(-self.minor_axis_size_in_mm / 2,
        #                                self.minor_axis_size_in_mm / 2)
        # minor_axis.plot(ax=ax)
        for piece in self.pieces:
            piece.plot(ax=ax)
        return ax

    @plot_data_view(selector="Pattern")
    def plot_data(self):
        """
        Dessia plot_data method
        return a PrimitiveGroup object
        """
        primitives = []
        for piece in self.pieces:
            primitives.append(piece.plot_data())
        primitive_group = plot_data.PrimitiveGroup(primitives)
        return primitive_group


class PatternGenerator(DessiaObject):
    _standalone_in_db = True
    _eq_is_data_eq = True
    _non_serializable_attributes = []
    _non_eq_attributes = ['name']
    _non_hash_attributes = ['name']
    """Responsable for Generating Patterns"""

    def __init__(self, minor_axis_size_in_mm: float,
                 diameters: List[float],
                 excentricity_min_max: Tuple[float, float],
                 diameter_percetage_clearence_min_max: Tuple[float, float] = (
                         0.1, 0.6),
                 name: str = ''):
        self.minor_axis_size_in_mm = minor_axis_size_in_mm
        self.diameters = diameters
        self.excentricity_min_max = excentricity_min_max
        self.diameter_percetage_clearence_min_max = \
            diameter_percetage_clearence_min_max
        # self.minor_axis_size_in_mm = minor_axis_size_in_mm
        # self.excentricity = excentricity
        # self.clearence = clearence
        # self.piece_diameter = piece_diameter
        self._utd_arclength = False
        self._utd_major_axis = False
        DessiaObject.__init__(self, name=name)

    # def orbital_piece_coordinates(self, phi):
    #     x_coordinate = (self.minor_axis_size_in_mm / 2) * math.sin(phi)
    #     y_coordinate = (self.major_axis / 2) * math.cos(phi)
    #     return volmdlr.Point2D(x_coordinate, y_coordinate)

    # def _create_path_from_force(self, force, point1, point2):
    #     tangent1 = point1.normal_vector()
    #     tangent1.normalize()
    #     tangent2 = -point2.normal_vector()
    #     tangent2.normalize()
    #     point1_t = point1 + force * tangent1
    #     point2_t = point2 + force * tangent2
    #
    #     points = [point1, point1_t, point2_t, point2]
    #
    #     bezier_curve = vme.BezierCurve2D(degree=3,
    #                                      control_points=points,
    #                                      name='bezier curve 1')
    #     return vmw.Wire2D([bezier_curve])
    #
    # def _path(self, point1, point2):
    #
    #     def find_force(force, point_1, point_2, targeted_length):
    #         bezier_curve = self._create_path_from_force(force, point_1, point_2)
    #         return bezier_curve.length() - targeted_length
    #
    #     res = bisect(find_force, 1e-6, (self.elipse_circunference / 4) * 2,
    #                  args=(point1, point2, self.elipse_circunference / 4))
    #
    #     bezier_curve = self._create_path_from_force(res, point1, point2)
    #
    #     return bezier_curve.primitives[0]

    def generate(self):
        """
        generates patterns
        """
        list_patterns = []
        for piece_diameter in self.diameters:
            clearence_min_max = [
                piece_diameter * self.diameter_percetage_clearence_min_max[0],
                piece_diameter * self.diameter_percetage_clearence_min_max[1]]
            for excentricity in np.linspace(self.excentricity_min_max[0],
                                            self.excentricity_min_max[1], 7):
                for clearence in np.linspace(clearence_min_max[0],
                                             clearence_min_max[1], 10):
                    # self.piece_diameter = piece_diameter
                    # self.excentricity = excentricity
                    # self.clearence = clearence
                    # horizontal_pieces = self.get_minor_axis_pieces()
                    # orbital_pieces = self.get_orbital_pieces(
                    #     piece_diameter)
                    list_patterns.append(Pattern(self.minor_axis_size_in_mm,
                                                 excentricity, clearence,
                                                 piece_diameter))

        return list_patterns

# class PatternResults(DessiaObject):
#     def __init__(self, list_patterns: List[Pattern],
#                  name: str = ''):
#         self.list_patterns = list_patterns
#         DessiaObject.__init__(self, name=name)
#
#     def plot_data(self):
#         points = []
#         for solution in self.list_patterns:
#             points.append({'minor_axis': solution.minor_axis_size_in_mm,
#                            'excentricity': solution.excentricity,
#                            'clearence': solution.clearence,
#                            'piece_diameter': solution.piece_diameter})
