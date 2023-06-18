from parapy.core import *
from parapy.geom import *
from math import radians, tan, pi, sin, atan, cos
from liftingsurface import LiftingSurface
from ref_frame import Frame
from winglet import Winglet
import os
from parapy.core.validate import Range

DIR = os.path.dirname(__file__)


class WingAssembly(GeomBase):
    w_c_root = Input(0.4243)
    w_c_tip = Input(0.4243/2)
    airfoil_root = Input('whitcomb')
    airfoil_tip = Input('whitcomb')
    t_factor_root = Input(2)
    t_factor_tip = Input(1)
    w_semi_span = Input(1.0259)
    sweep_le = Input(25)
    twist = Input(-2)
    fu_width = Input(0.3340)
    winglet_thickness = Input(0.005, validator=Range(0.002, 0.01))
    elevon_chord_factor = Input(0.3, validator=Range(0.2, 0.5))
    elevon_span_factor = Input(0.4, validator=Range(0.3, 0.8))
    elevon_spanwise_pos = Input(0.1, validator=Range(0.03, 0.2))

    @Part
    def main_wing(self):
        return LiftingSurface(
            w_c_root=self.w_c_root,
            w_c_tip=self.w_c_tip,
            airfoil_root=self.airfoil_root,
            airfoil_tip=self.airfoil_tip,
            t_factor_root=self.t_factor_root,
            t_factor_tip=self.t_factor_tip,
            w_semi_span=self.w_semi_span,
            sweep=self.sweep_le,
            twist=self.twist,
            position=translate(self.position, 'y', self.fu_width / 2),
            mesh_deflection=0.0001,
            color="white",
            hidden=True
        )

    @Attribute
    def sweep_te(self):
        return atan((self.w_semi_span * tan(radians(self.sweep_le)) + self.w_c_tip - self.w_c_root) / self.w_semi_span)

    @Attribute
    def hinge_radius(self):
        return 0.8 * self.w_c_tip * (self.t_factor_root+self.t_factor_tip)/4


    def elevon_span(self):
        return self.elevon_span_factor * self.w_semi_span

    @Attribute
    def elevon_chord(self):
        return self.elevon_chord_factor * self.w_c_tip

    @Attribute
    def elevon_position2(self):
        return rotate(translate(self.position,
                                'x', self.w_c_root - tan(self.sweep_te)*self.fu_width/2,
                                #'y', self.fu_width / 2 + self.w_semi_span / 2,
                                'z', -0.5 * (self.w_c_root + self.w_c_tip) * sin(radians(self.twist / 2))),
                      'z', -self.sweep_te)

    @Attribute
    def elevon_position3(self):
        return rotate(translate(self.position,
                                'x', self.w_c_root + self.w_semi_span / 2 * sin(self.sweep_te),
                                'y', self.fu_width / 2 + self.w_semi_span / 2,
                                'z', -0.5 * (self.w_c_root + self.w_c_tip) * sin(radians(self.twist / 2))),
                      'z', -self.sweep_te)

    @Attribute
    def elevon_position4(self):
        return rotate(translate(self.position,
                                      'x', 0.6*self.w_c_root,
                                      'y', (0.5 * self.fu_width + self.w_semi_span)*(1-self.elevon_spanwise_pos),
                                      'z', -0.6 * self.w_c_tip),
                    'z',3/2*pi)

    @Part
    def hinge_frame(self):
        return Frame(pos=self.elevon_position2,
                     hidden=True
                     )

    @Part
    def hinge_frame2(self):
        return Frame(pos=self.elevon_position4,
                     hidden=True
            )

    @Part
    def hinge_cylinder(self):
        return Cylinder(
            radius=self.hinge_radius,
            height= 1.2*self.w_semi_span,
            angle=pi * 2,
            position=rotate(translate(self.elevon_position2,
                                      'x', -self.elevon_chord+self.hinge_radius,
                                      'y', self.fu_width/2/cos(self.sweep_te)),
                            'x', radians(270)),
            hidden=True
        )

    @Part
    def elevon_box1(self):
        return Box(width=self.w_c_tip,
                   length=1.2*self.w_semi_span,
                   height=self.hinge_radius * 2,
                   position=translate(self.elevon_position2,
                                      'x', -self.elevon_chord+self.hinge_radius,
                                      'y', self.fu_width/2/cos(self.sweep_te),
                                      'z', -self.hinge_radius),
                   hidden=True
                   )

    @Part
    def elevon_box_cylinder1(self):
        return FusedSolid(shape_in=self.hinge_cylinder,
                          tool=self.elevon_box1,
                          hidden=True
                          )

    @Part
    def elevon_box2(self):
        return Box(width=0.5 * self.w_semi_span,
                   length=0.3 * self.w_semi_span,  # spanwise elevon length
                   height=0.2 * self.w_semi_span,
                   position=translate(self.position,
                                      'x', self.w_c_root,
                                      'y', 0.7 * self.fu_width + self.w_semi_span / 2,
                                      'z', -0.6 * self.w_c_tip),
                   hidden=True
                   )

    @Part
    def elevon_box3(self):
        return Box(width=self.elevon_span_factor * self.w_semi_span,
                   length=0.8 * self.w_semi_span,  # spanwise elevon length
                   height=0.2 * self.w_semi_span,
                   position=self.elevon_position4,
                   hidden=True
                   )

    @Part
    def elevon_box_cylinder2(self):
        return CommonSolid(shape_in=self.elevon_box_cylinder1,
                           tool=self.elevon_box3,
                           hidden=True
                           )

    @Part
    def wing_right(self):
        return SubtractedSolid(shape_in=self.main_wing,
                               tool=self.elevon_box_cylinder2,
                               mesh_deflection=0.0001,
                               color="white"
                               )

    @Part
    def wing_left(self):
        return MirroredShape(
            shape_in=self.wing_right,
            reference_point=self.position,
            vector1=self.position.Vz,
            vector2=self.position.Vx,
            mesh_deflection=0.0001,
            color="white"
        )

    @Part
    def elevon_right(self):
        return CommonSolid(shape_in=self.main_wing,
                           tool=self.elevon_box_cylinder2,
                           color="gray")

    @Part
    def elevon_left(self):
        return MirroredShape(
            shape_in=self.elevon_right,
            reference_point=self.position,
            vector1=self.position.Vz,
            vector2=self.position.Vx,
            mesh_deflection=0.0001,
            color="gray"
        )

    @Part
    def winglet(self):
        return Winglet(
            chord=self.w_c_tip,
            xpos=self.w_semi_span * tan(radians(self.sweep_le)) + self.w_c_tip / 2,
            ypos=self.fu_width / 2 + self.w_semi_span + self.winglet_thickness,
            color="white",
        )


if __name__ == '__main__':
    from parapy.gui import display

    obj = WingAssembly()
    display(obj)
