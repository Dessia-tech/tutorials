import math
import random
from typing import List

import plot_data.core as plot_data
import volmdlr as vm
from dessia_common.core import DessiaObject
from plot_data.colors import *


class Graphs(DessiaObject):
    _standalone_in_db = True

    def __init__(self, amplitude: float, number: int, name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.number = number
        self.amplitude = amplitude

        self.x = [i / (2 * math.pi) for i in range(number)]
        self.y1 = [self.amplitude * math.sin(i) for i in self.x]
        self.y2 = [self.amplitude * math.cos(i) for i in self.x]

    def data_set1(self):
        attributes = ['x', 'y']
        tooltip = plot_data.Tooltip(attributes=attributes)
        point_style = plot_data.PointStyle(color_fill=RED, color_stroke=BLACK)
        edge_style = plot_data.EdgeStyle(color_stroke=BLUE, dashline=[10, 5])
        elements = []
        for x, y in zip(self.x, self.y1):
            elements.append({'x': x, 'y': y})
        return plot_data.Dataset(elements=elements, name='y = sin(x)',
                                 tooltip=tooltip, point_style=point_style,
                                 edge_style=edge_style)

    def data_set2(self):
        attributes = ['x', 'y']
        tooltip = plot_data.Tooltip(attributes=attributes)
        point_style = plot_data.PointStyle(color_fill=GREEN,
                                           color_stroke=BLACK)
        edge_style = plot_data.EdgeStyle(color_stroke=BLUE, dashline=[10, 5])
        elements = []
        for x, y in zip(self.x, self.y2):
            elements.append({'x': x, 'y': y})
        return plot_data.Dataset(elements=elements, name='y = cos(x)',
                                 tooltip=tooltip, point_style=point_style,
                                 edge_style=edge_style)

    def plot_data(self):
        data_sets = [self.data_set1(), self.data_set2()]
        graphs2d = plot_data.Graph2D(graphs=data_sets,
                                     x_variable='x', y_variable='y')
        return graphs2d


class ScatterPlot(DessiaObject):
    _standalone_in_db = True

    def __init__(self, maximum_x: float, maximum_y: float, name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.maximum_x = maximum_x
        self.maximum_y = maximum_y

        points = []
        for i in range(500):
            x = random.uniform(0, self.maximum_x)
            y = random.uniform(0, self.maximum_y)
            points.append({'x': x, 'y': y})
        self.points = points

    def plot_data(self):
        color_fill = LIGHTBLUE
        color_stroke = GREY
        point_style = plot_data.PointStyle(color_fill=color_fill,
                                           color_stroke=color_stroke)
        axis = plot_data.Axis()
        attributes = ['x', 'y']
        tooltip = plot_data.Tooltip(attributes=attributes)
        return plot_data.Scatter(tooltip=tooltip, x_variable=attributes[0],
                                 y_variable=attributes[1],
                                 point_style=point_style,
                                 elements=self.points, axis=axis)


class ParallelPlot(DessiaObject):
    _standalone_in_db = True

    def __init__(self, maximum_x: float, maximum_y: float, name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.maximum_x = maximum_x
        self.maximum_y = maximum_y

        points = []
        for i in range(5):
            x = random.uniform(0, self.maximum_x)
            y = random.uniform(0, self.maximum_y)
            z = random.uniform(0, self.maximum_y)
            m = random.uniform(0, self.maximum_y)
            points.append({'x': x, 'y': y, 'z': z, 'm': m})
        self.points = points

    def plot_data(self):
        edge_style = plot_data.EdgeStyle()
        rgbs = [[192, 11, 11], [14, 192, 11], [11, 11, 192]]
        return plot_data.ParallelPlot(elements=self.points,
                                      edge_style=edge_style,
                                      disposition='vertical',
                                      axes=['x', 'y', 'z', 'm'],
                                      rgbs=rgbs)


class MultiPlot(DessiaObject):
    _standalone_in_db = True

    def __init__(self, maximum_x: float, maximum_y: float, name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.maximum_x = maximum_x
        self.maximum_y = maximum_y

        points = []
        for i in range(500):
            x = random.uniform(0, self.maximum_x)
            y = random.uniform(0, self.maximum_y)
            z = random.uniform(0, self.maximum_y)
            m = random.uniform(0, self.maximum_y)
            points.append({'x': x, 'y': y, 'z': z, 'm': m})
        self.points = points

    def plot_data(self):
        color_fill = LIGHTBLUE
        color_stroke = GREY
        point_style = plot_data.PointStyle(color_fill=color_fill,
                                           color_stroke=color_stroke)
        axis = plot_data.Axis()
        attributes = ['x', 'y']
        tooltip = plot_data.Tooltip(attributes=attributes)
        objects = [plot_data.Scatter(tooltip=tooltip, x_variable=attributes[0],
                                     y_variable=attributes[1],
                                     point_style=point_style,
                                     elements=self.points, axis=axis)]

        edge_style = plot_data.EdgeStyle()
        rgbs = [[192, 11, 11], [14, 192, 11], [11, 11, 192]]
        objects.append(plot_data.ParallelPlot(elements=self.points,
                                              edge_style=edge_style,
                                              disposition='vertical',
                                              axes=['x', 'y', 'z', 'm'],
                                              rgbs=rgbs))

        coords = [(0, 0), (500, 0)]
        sizes = [plot_data.Window(width=500, height=500),
                 plot_data.Window(width=500, height=500)]

        return plot_data.MultiplePlots(elements=self.points, plots=objects,
                                       sizes=sizes, coords=coords)


class SimpleShape(DessiaObject):
    _standalone_in_db = True

    def __init__(self, lx: float, ly: float, name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.lx = lx
        self.ly = ly

    def plot_data(self):
        hatching = plot_data.HatchingSet(0.5, 3)
        edge_style = plot_data.EdgeStyle(line_width=1, color_stroke=BLUE,
                                         dashline=[])
        surface_style = plot_data.SurfaceStyle(color_fill=WHITE, opacity=1,
                                               hatching=hatching)

        pt1 = vm.Point2D(0, 0)
        pt2 = vm.Point2D(0, self.ly)
        pt3 = vm.Point2D(self.lx, self.ly)
        pt4 = vm.Point2D(self.lx, 0)
        c1 = vm.wires.Contour2D([vm.edges.LineSegment2D(pt1, pt2),
                                 vm.edges.LineSegment2D(pt2, pt3),
                                 vm.edges.LineSegment2D(pt3, pt4),
                                 vm.edges.LineSegment2D(pt4, pt1)])
        contours = [c1]
        for i in range(5):
            vector = vm.Vector2D(random.uniform(0, 2), random.uniform(0, 2))
            c2 = c1.translation(vector, copy=True)
            contours.append(c2)

        plot_datas = [c.plot_data(edge_style=edge_style,
                                  surface_style=surface_style)
                      for c in contours]
        return plot_data.PrimitiveGroup(primitives=plot_datas)


class ScatterPlotList(DessiaObject):
    _standalone_in_db = True

    def __init__(self, posx: List[float], posy: List[float], name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.posx = posx
        self.posy = posy
        points = []
        for x, y in zip(posx, posy):
            points.append({'x': x, 'y': y})
        self.points = points

    def plot_data(self):
        color_fill = LIGHTBLUE
        color_stroke = GREY
        point_style = plot_data.PointStyle(color_fill=color_fill,
                                           color_stroke=color_stroke)
        axis = plot_data.Axis()
        attributes = ['x', 'y']
        tooltip = plot_data.Tooltip(attributes=attributes)
        return plot_data.Scatter(tooltip=tooltip, x_variable=attributes[0],
                                 y_variable=attributes[1],
                                 point_style=point_style,
                                 elements=self.points, axis=axis)
