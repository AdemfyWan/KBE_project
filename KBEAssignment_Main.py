

from math import tan, radians, pi
from parapy.core import *
from parapy.geom import *
from ref_frame import Frame
from liftingsurface import LiftingSurface


crootin = 1.1

class Aircraft(GeomBase):

    fu_width = Input(0.9)  # fuselage width

    # wing geometry
    w_c_root = Input(crootin)
    w_c_tip = Input(0.5)
    w_semi_span = Input(2.5)
    sweep = Input(25)
    twist = Input(0)
    wing_dihedral = Input(0)

    # root & tip airfoil geometry
    airfoil_root = Input("whitcomb")
    airfoil_tip = Input("whitcomb")
    #: to reduce/increase the thickness of the airfoil from the .dat file
    t_factor_root = Input(1.4)
    t_factor_tip = Input(1)

    # motor
    mot_mount_h = Input(0.15)
    mot_mount_w = Input(0.05)
    mot_mount_l = Input(0.15)

    @Part
    def aircraft_frame(self):
        return Frame(pos=self.position)

    @Part
    def right_wing(self):
        return LiftingSurface(
            pass_down="airfoil_root, airfoil_tip, w_c_root, w_c_tip,"
                      "t_factor_root, t_factor_tip, w_semi_span, "
                      "sweep, twist",
            # position=rotate(
            #     translate  # longitudinal and vertically translation w.r.t. fuselage
            #     (self.position,
            #      "x", self.wing_position_fraction_long * self.fu_length,
            #      "z", self.wing_position_fraction_vrt * - self.fu_radius),
            # #     "x", radians(self.wing_dihedral)
            # ),
            # dihedral applied by rigid rotation
            position=translate(self.position, 'y', self.fu_width / 2),
            mesh_deflection=0.0001,
            color="gray"
        )

    @Part
    def left_wing(self):
        return MirroredShape(
            shape_in=self.right_wing,
            reference_point=self.position,
            vector1=self.position.Vz,
            vector2=self.position.Vx,
            mesh_deflection=0.0001,
            color="gray"
        )

    @Part
    def body(self):
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
            color="gray"
        )

    @Part
    def motormount(self):
        return Box(
            height=self.mot_mount_h,
            width=self.mot_mount_w,
            length=self.mot_mount_l,
            position=translate(self.position,
                               'y', -1 * self.mot_mount_l / 2,
                               'x', self.w_c_root-self.mot_mount_w),
            color="gray")

    @Part
    def motor(self):
        return Cylinder(
            radius=self.mot_mount_h / 2,
            height=self.mot_mount_w * 2,
            angle=pi*2,
            position=rotate90(translate(self.position,
                                        'x', self.w_c_root,
                                        'z', self.mot_mount_h / 2),
                              'y'),
            color="orange"
        )


if __name__ == '__main__':
    from parapy.gui import display
    obj = Aircraft(label="aircraft")
    display(obj)
