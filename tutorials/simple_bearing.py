import math
from math import cos, pi, sin

from dessia_common.core import PhysicalObject
from dessia_common.decorators import plot_data_view, cad_view
from plot_data import EdgeStyle, PrimitiveGroup, SurfaceStyle
from plot_data.colors import BLACK, GREY
from volmdlr import OXYZ, Z3D, Point2D, Point3D, Frame3D, Vector3D
from volmdlr.core import VolumeModel
from volmdlr.curves import Circle2D
from volmdlr.primitives3d import ExtrudedProfile
from volmdlr.wires import Contour2D
from volmdlr.shapes import Solid


class Ball(PhysicalObject):
    _standalone_in_db = False

    def __init__(self, diameter: float, name: str = ''):
        self.diameter = diameter
        PhysicalObject.__init__(self, name=name)

    def volmdlr_primitives(self, pos_x=0., pos_y=0., pos_z=0.,
                           distance=0., angle=0.):
        center_x = pos_x + distance * math.cos(angle)
        center_y = pos_y + distance * math.sin(angle)
        center_z = pos_z
        center = (center_x, center_y, center_z)

        u_axis = Vector3D(1, 0, 0)
        v_axis = Vector3D(0, 1, 0)
        w_axis = Vector3D(0, 0, 1)

        frame = Frame3D(
            origin=Point3D(*center),
            u=u_axis,
            v=v_axis,
            w=w_axis)

        sphere = Solid.make_sphere(
            radius=self.diameter / 2,
            frame=frame,
            angle1=-math.pi / 2,
            angle2=math.pi / 2,
            angle3=2 * math.pi,
            name='sphere')

        return [sphere]

    @plot_data_view("2D display for Ball")
    def display_2d(self, pos_x=0., pos_y=0., distance=0., angle=0.):
        # Color settings
        edge_style = EdgeStyle(color_stroke=BLACK)
        surface_style = SurfaceStyle(color_fill=GREY, opacity=0.5)

        ball_x = distance * cos(angle)
        ball_y = distance * sin(angle)
        center = Point2D(pos_x + ball_x, pos_y + ball_y)
        circle = Circle2D.from_center_and_radius(
            center=center, radius=self.diameter / 2)
        primitives = [circle.plot_data(
            edge_style=edge_style, surface_style=surface_style)]
        return PrimitiveGroup(primitives=primitives,
                              name='Circle')

    @cad_view(selector='Ball CAD')
    def cad_view(self):
        primitives = self.volmdlr_primitives()
        return VolumeModel(primitives=primitives).babylon_data()


class Bearing(PhysicalObject):
    _standalone_in_db = True

    def __init__(self, ball: Ball, internal_diameter: float,
                 external_diameter: float, height: float,
                 thickness: float = 0., name: str = ''):
        self.ball = ball
        self.internal_diameter = internal_diameter
        self.external_diameter = external_diameter
        self.height = height
        self.thickness = thickness
        PhysicalObject.__init__(self, name=name)

    def volmdlr_primitives(self, pos_x=0., pos_y=0., pos_z=0.,
                           number_balls=10):
        # Setup circles for extrusions
        outer_circle = Circle2D.from_center_and_radius(
            center=Point2D(pos_x, pos_y),
            radius=self.external_diameter / 2)
        inner_outer_circle = Circle2D.from_center_and_radius(
            center=Point2D(pos_x, pos_y),
            radius=self.external_diameter / 2 - self.thickness)
        inner_circle = Circle2D.from_center_and_radius(
            center=Point2D(pos_x, pos_y),
            radius=self.internal_diameter / 2)
        outer_inner_circle = Circle2D.from_center_and_radius(
            center=Point2D(pos_x, pos_y),
            radius=self.internal_diameter / 2 + self.thickness)
        # Extrusions
        frame = OXYZ.copy()
        frame.origin += Z3D * (pos_z - self.height/2)
        outer_extrusion = Solid.make_extrusion_from_frame_and_wires(
            frame=frame, extrusion_length=self.height, outer_contour2d=Contour2D.from_circle(outer_circle),
            inner_contours2d=[Contour2D.from_circle(inner_outer_circle)])
        inner_extrusion = Solid.make_extrusion_from_frame_and_wires(
            frame=frame, extrusion_length=self.height, outer_contour2d=Contour2D.from_circle(outer_inner_circle),
            inner_contours2d=[Contour2D.from_circle(inner_circle)])
        # Balls
        ball_primitives = []
        ball_distance = self.internal_diameter / 2 + \
            (self.external_diameter - self.internal_diameter) / 4
        for i in range(number_balls):
            ball_primitive = self.ball.volmdlr_primitives(
                pos_x=pos_x, pos_y=pos_y, pos_z=pos_z,
                distance=ball_distance,
                angle=i * 2 * pi / number_balls)[0]
            ball_primitives.append(ball_primitive)
        return [outer_extrusion, inner_extrusion] + ball_primitives

    @plot_data_view("2D display for Bearing")
    def display_2d(self, pos_x=0., pos_y=0., number_balls=10):
        # Color settings
        edge_style = EdgeStyle(color_stroke=BLACK)
        surface_style = SurfaceStyle(opacity=0)

        primitives = []
        center = Point2D(pos_x, pos_y)
        # External circle
        external_circle = Circle2D.from_center_and_radius(
            center=center, radius=self.external_diameter / 2)
        primitives.append(external_circle.plot_data(
            edge_style=edge_style, surface_style=surface_style))
        # Internal circle
        internal_circle = Circle2D.from_center_and_radius(
            center=center, radius=self.internal_diameter / 2)
        primitives.append(internal_circle.plot_data(
            edge_style=edge_style, surface_style=surface_style))
        # Balls
        ball_distance = self.internal_diameter / 2 + \
            (self.external_diameter - self.internal_diameter) / 4
        for i in range(number_balls):
            primitives.extend(self.ball.display_2d(
                pos_x=pos_x,
                pos_y=pos_y,
                distance=ball_distance,
                angle=i * 2 * pi / number_balls).primitives)
        return PrimitiveGroup(primitives=primitives)

    @cad_view(selector='Bearing CAD')
    def cad_view(self):
        primitives = self.volmdlr_primitives()
        return VolumeModel(primitives=primitives).babylon_data()

    def to_markdown(self):
        infos = '## Bearing Infos \n\n'
        infos += '|name|height|external_diameter|internal_diameter|' + '\n'
        infos += '|:---------:|:---------:|:---------:|:---------:|' + '\n'
        infos += '|' + self.name + '|' + str(self.height) + '|' \
                 + str(self.external_diameter) \
                 + '|' + str(self.internal_diameter) + '|\n'
        return infos
