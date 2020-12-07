import volmdlr as vm
import volmdlr.primitives2d as p2d
import volmdlr.primitives3d as p3d
import plot_data.core as plot_data
import math
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

    def __init__(self, name: str = ''):
        DessiaObject.__init__(self, name=name)

    def plot_data(self):
        width = 2
        height = 1

        # Shape set (circle, square, crux)
        shape = 'circle'

        # Point size (1 to 4)
        size = 2

        # Points' color
        colorfill = LIGHTBLUE
        colorstroke = GREY

        strokewidth = 0.5
        # Scatter plot
        nb_points_x = 10
        nb_points_y = 10
        font_size = 12
        graduation_color = GREY
        axis_color = GREY
        axis_width = 0.5
        arrow_on = False
        grid_on = True

        # Tooltip
        tp_colorfill = GREY
        text_color = WHITE
        # Font family : Arial, Helvetica, serif, sans-serif,
        # Verdana, Times New Roman, Courier New
        tl_fontsize = 12
        tl_fontstyle = 'sans-serif'
        tp_radius = 5
        to_display_att_names = ['cx', 'cy']
        opacity = 0.75

        axis = plot_data.Axis(nb_points_x=nb_points_x, nb_points_y=nb_points_y,
                              font_size=font_size, graduation_color=graduation_color,
                              axis_color=axis_color, arrow_on=arrow_on,
                              axis_width=axis_width, grid_on=grid_on)

        tooltip = plot_data.Tooltip(colorfill=tp_colorfill, text_color=text_color,
                                    fontsize=tl_fontsize, fontstyle=tl_fontstyle,
                                    tp_radius=tp_radius,
                                    to_plot_list=to_display_att_names, opacity=opacity)

        # plot_datas = []
        point_list = []
        color_fills = [VIOLET, BLUE, GREEN, RED, YELLOW, CYAN, ROSE]
        for i in range(500):
            cx = random.uniform(0, 2)
            cy = random.uniform(0, 1)
            random_color_fill = color_fills[random.randint(0, len(color_fills) - 1)]
            point = plot_data.Point2D(cx=cx, cy=cy, size=size, shape=shape,
                                      color_fill=random_color_fill,
                                      color_stroke=colorstroke,
                                      stroke_width=strokewidth)
            point_list += [point]

        return plot_data.Scatter(elements=point_list, axis=axis,
                                         tooltip=tooltip,
                                         to_display_att_names=to_display_att_names,
                                         point_shape=shape, point_size=size,
                                         color_fill=colorfill,
                                         color_stroke=colorstroke,
                                         stroke_width=strokewidth)