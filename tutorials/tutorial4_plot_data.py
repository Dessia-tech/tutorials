import volmdlr as vm
import volmdlr.primitives2d as p2d
import volmdlr.primitives3d as p3d
import plot_data.core as plot_data
import math
import numpy as np
from itertools import product
from plot_data.colors import *

from dessia_common import DessiaObject
from typing import List
import random


class Graph(DessiaObject):
    _standalone_in_db = True

    def __init__(self, amplitude: float, number:int, name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.number = number
        self.amplitude = amplitude

        self.x = [i/(2*math.pi) for i in range(number)]
        self.y = [self.amplitude*math.sin(i) for i in self.x]

    def plot_data(self):
        points = []
        for x, y in zip(self.x, self.y):
            points.append(plot_data.Point2D(x, y, size=2,
                              shape='square', color_fill=BROWN,
                              color_stroke=BLACK,
                              stroke_width=0.5))

        # Tooltip
        colorfill = BLACK
        text_color = WHITE
        tl_fontsize = 12  # Font family : Arial, Helvetica, serif, sans-serif, Verdana, Times New Roman, Courier New
        tl_fontstyle = 'sans-serif'
        tp_radius = 5
        to_plot_list = ['cx', 'cy']
        opacity = 0.75
        tooltip = plot_data.Tooltip(colorfill=colorfill, text_color=text_color,
                                    fontsize=tl_fontsize, fontstyle=tl_fontstyle,
                                    tp_radius=tp_radius, to_plot_list=to_plot_list,
                                    opacity=opacity)

        graph = plot_data.Dataset(points=points, dashline=[5, 3, 1, 3],
                                   graph_colorstroke=BLUE, graph_linewidth=0.5,
                                   display_step=2, tooltip=tooltip, name='Graph')

        return plot_data.Graph2D(graphs=[graph])

class ScatterPlot(DessiaObject):
    _standalone_in_db = True

    def __init__(self, maximum_x:float, maximum_y: float, name: str = ''):
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
        axis = plot_data.Axis(nb_points_x=10, nb_points_y=10,
                              font_size=12, graduation_color=GREY,
                              axis_color=GREY, arrow_on=False,
                              axis_width=0.5, grid_on=True)

        tooltip = plot_data.Tooltip(colorfill=GREY, text_color=WHITE,
                                    fontsize=12, fontstyle='sans-serif',
                                    tp_radius=5,
                                    to_plot_list=['x', 'y'], opacity=0.75)

        return plot_data.Scatter(elements=self.points, axis=axis,
                                         tooltip=tooltip,
                                         to_display_att_names=['x', 'y'],
                                         point_shape='circle', point_size=2,
                                         color_fill=LIGHTBLUE,
                                         color_stroke=GREY,
                                         stroke_width=0.5)

class ParallelPlot(DessiaObject):
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
        axis = plot_data.Axis(nb_points_x=10, nb_points_y=10,
                              font_size=12, graduation_color=GREY,
                              axis_color=GREY, arrow_on=False,
                              axis_width=0.5, grid_on=True)

        tooltip = plot_data.Tooltip(colorfill=GREY, text_color=WHITE,
                                    fontsize=12, fontstyle='sans-serif',
                                    tp_radius=5,
                                    to_plot_list=['x', 'y'], opacity=0.75)

        rgbs = [[192, 11, 11], [14, 192, 11], [11, 11, 192]]
        return plot_data.ParallelPlot(elements=self.points,
                                               line_color=BLACK,
                                               line_width=0.5,
                                               disposition='vertical',
                                               to_disp_attributes=['x', 'y', 'z', 'm'],
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
        axis = plot_data.Axis(nb_points_x=10, nb_points_y=10,
                              font_size=12, graduation_color=GREY,
                              axis_color=GREY, arrow_on=False,
                              axis_width=0.5, grid_on=True)

        tooltip = plot_data.Tooltip(colorfill=GREY, text_color=WHITE,
                                    fontsize=12, fontstyle='sans-serif',
                                    tp_radius=5,
                                    to_plot_list=['x', 'y'], opacity=0.75)
        objects = [plot_data.Scatter(elements=self.points, axis=axis,
                          tooltip=tooltip,
                          to_display_att_names=['x', 'y'],
                          point_shape='circle', point_size=2,
                          color_fill=LIGHTBLUE,
                          color_stroke=GREY,
                          stroke_width=0.5)]

        rgbs = [[192, 11, 11], [14, 192, 11], [11, 11, 192]]
        objects.append(plot_data.ParallelPlot(elements=self.points,
                                               line_color=BLACK,
                                               line_width=0.5,
                                               disposition='vertical',
                                               to_disp_attributes=['x', 'y', 'z', 'm'],
                                               rgbs=rgbs))

        coords = [(0, 0), (300, 0)]
        sizes = [plot_data.Window(width=560, height=300),
                 plot_data.Window(width=560, height=300)]

        return plot_data.MultiplePlots(points=self.points, objects=objects,
                                                sizes=sizes, coords=coords)


class SimpleShape(DessiaObject):
    _standalone_in_db = True

    def __init__(self, lx: float, ly: float, name: str = ''):
        DessiaObject.__init__(self, name=name)
        self.lx = lx
        self.ly = ly

    def plot_data(self):
        hatching = plot_data.HatchingSet(1)
        plot_data_state = plot_data.Settings(name='name', hatching=hatching,
                                             stroke_width=1)

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
            c2 = c1.translation(vm.Vector2D(random.uniform(0,2), random.uniform(0,2)), copy=True)
            contours.append(c2)

        plot_datas = [c.plot_data(plot_data_states=[plot_data_state]) for c in contours]
        return plot_data.PrimitiveGroup(contours=plot_datas)
