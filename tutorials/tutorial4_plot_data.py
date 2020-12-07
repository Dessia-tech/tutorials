import volmdlr as vm
import volmdlr.primitives2d as p2d
import volmdlr.primitives3d as p3d
import plot_data.core as plot_data
import math
from itertools import product
from plot_data.colors import *

from dessia_common import DessiaObject
from typing import List


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