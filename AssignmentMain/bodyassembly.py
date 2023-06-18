from parapy.core import *
from parapy.geom import *
from parapy.core.validate import Range
from math import atan, sqrt
import numpy as np
from liftingsurface import LiftingSurface
import os

DIR = os.path.dirname(__file__)


class BodyAssembly(GeomBase):
    w_c_root = Input(0.4243)
    t_factor_root = Input(2)
    airfoil_root = Input('hs522')
    fu_width = Input(0.3340)
    sweep_le = Input(25)
    w_semi_span = Input(1.0259)
    compartment_length_ratio = Input(0.5, validator=Range(0.3, 0.5))
    motor_mount_length_ratio = Input(0.35, validator=Range(0.05, 0.39))
    motor_radius = Input(0.016786)

# BODY & COMPARTMENT ===================================================================================================

    @Attribute
    def root_zmax_z(self):
        return max(self.body_full.root_airfoil.z_points)

    @Attribute
    def root_zmax_x(self):
        zmax_index = self.body_full.root_airfoil.z_points.index(self.root_zmax_z)
        return self.body_full.root_airfoil.x_points[zmax_index]

    @Part
    def body_full(self):
        return LiftingSurface(
            w_c_root=self.w_c_root,
            w_c_tip=self.w_c_root,
            airfoil_root=self.airfoil_root,
            airfoil_tip=self.airfoil_root,
            t_factor_root=self.t_factor_root,
            t_factor_tip=self.t_factor_root,
            w_semi_span=self.fu_width,
            sweep=0,
            twist=0,
            position=translate(self.position, 'y', -1 * self.fu_width / 2),
            mesh_deflection=0.0001,
            color="white",
            hidden=True
        )

    @Part
    def compartment_box1(self):
        return Box(
            height=self.root_zmax_z + 0.001,  # z
            length=self.fu_width * 0.75,  # y
            width=self.w_c_root * self.compartment_length_ratio,  # x
            position=translate(self.position,
                               'x', self.w_c_root * 0.1 + self.w_c_root * self.compartment_length_ratio / 2,  # (croot * distance to tip) + (croot * compartmentwidth/2)
                               'z', self.root_zmax_z / 2),
            centered=True,
            color="red",
            hidden=True)

    @Part
    def compartment_box2(self):
        return Box(
            height=self.root_zmax_z + 0.001,  # z
            length=self.fu_width * 0.75,  # y
            width=self.w_c_root * self.compartment_length_ratio-0.01,  # x
            position=translate(self.position,
                               'x', self.w_c_root * 0.1 + self.w_c_root * self.compartment_length_ratio / 2,  # (croot * distance to tip) + (croot * compartmentwidth/2)
                               'z', self.root_zmax_z / 2),
            centered=True,
            color="Blue",
            hidden=True)

    @Part
    def compartment_full(self):
        return CommonSolid(shape_in=self.body_full,
                           tool=self.compartment_box1,
                           color="gray",
                           hidden=True,
                           )

    @Part
    def compartment_translated(self):
        return TranslatedShape(shape_in=self.compartment_full,
                               displacement=Vector(0, 0, -0.003),
                               color='red',
                               hidden=True)

    @Part
    def compartment_cover(self):
        return SubtractedSolid(shape_in=self.compartment_full,
                               tool=self.compartment_translated,
                               mesh_deflection=0.0001,
                               color="gray",
                               transparency=0.5,
                               hidden=False
                               )

    @Part
    def body_cut1(self):
        return SubtractedSolid(shape_in=self.body_full,
                               tool=self.compartment_cover,
                               mesh_deflection=0.0001,
                               color="white",
                               hidden=True
                               )

    @Part
    def main_body(self):
        return SubtractedSolid(shape_in=self.body_cut1,
                               tool=self.compartment_box2,
                               mesh_deflection=0.0001,
                               color="white",
                               hidden=False
                               )

    # @Part
    # def section_box(self):
    #     return Box(
    #         height=5,  # z
    #         length=5,  # y
    #         width=5,  # x
    #         position=translate(self.position,
    #                            'z', -2.5,
    #                            'x', -2.5),
    #         centered=False,
    #         color="Blue",
    #         hidden=True)
    #
    # @Part
    # def body_section(self):
    #     return SubtractedSolid(shape_in=self.main_body,
    #                            tool=self.section_box,
    #                            mesh_deflection=0.0001,
    #                            color="white",
    #                            hidden=False
    #                            )

# MOTOR MOUNT ==========================================================================================================

    @Attribute
    def mot_mount_s(self):
        return self.motor_radius*2*1.1

    @Attribute
    def mot_mount_h(self):
        return max(self.mot_mount_s, self.mot_mount_anchor_z)

    @Attribute
    def mot_mount_t(self):
        return self.w_c_root-self.mot_mount_anchor_x

    @Attribute
    def mot_mount_anchor_x(self):
        return (1-self.motor_mount_length_ratio)*self.w_c_root

    @Attribute
    def mot_mount_anchor_z(self):
        half_index = self.body_full.root_airfoil.x_points.index(0)
        xp = list(reversed(self.body_full.root_airfoil.x_points[0:half_index]))
        fp = list(reversed(self.body_full.root_airfoil.z_points[0:half_index]))
        return np.interp(self.mot_mount_anchor_x, xp, fp)

    @Attribute
    def mot_mount_slope(self):
        x1 = self.mot_mount_anchor_x
        z1 = self.mot_mount_anchor_z
        x2 = self.w_c_root
        z2 = self.mot_mount_s
        return atan((z2-z1)/(x2-x1))

    @Attribute
    def mot_mount_slope_length(self):
        x1 = self.mot_mount_anchor_x
        z1 = self.mot_mount_anchor_z
        x2 = self.w_c_root
        z2 = self.mot_mount_s
        return sqrt((x2-x1)**2+(z2-z1)**2)

    @Part
    def motor_mount_box1(self):
        return Box(
            height=self.mot_mount_h,
            length=self.mot_mount_s,
            width=self.mot_mount_t,
            position=translate(self.position,
                               'y', -1 * self.mot_mount_s / 2,
                               'x', self.w_c_root - self.mot_mount_t),
            color="white",
            hidden=True)

    @Part
    def motor_mount_box2(self):
        return Box(
            height=self.mot_mount_s,
            length=self.mot_mount_s*1.1,
            width=self.mot_mount_slope_length,
            position=rotate(translate(self.motor_mount_box1.position,
                                      'y', -self.mot_mount_s*0.05,
                                      'z', self.mot_mount_anchor_z),
                            'y', -self.mot_mount_slope),
            color="green",
            hidden=True)

    @Part
    def motor_mount_box3(self):
        return SubtractedSolid(shape_in=self.motor_mount_box1,
                               tool=self.motor_mount_box2,
                               color="white",
                               hidden=False)

    @Part
    def motor_mount(self):
        return SubtractedSolid(shape_in=self.motor_mount_box3,
                               tool=self.body_full,
                               color="white")


if __name__ == '__main__':
    from parapy.gui import display

    obj = BodyAssembly()
    display(obj)
