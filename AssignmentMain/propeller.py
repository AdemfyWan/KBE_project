from parapy.core import *
from parapy.geom import *
from math import radians, pi, atan, degrees
from liftingsurface import LiftingSurface


class Propeller(GeomBase):
    w_c_root = Input(0.4243)
    p_twist = Input(35)
    p_taper = Input(0.008/0.018)
    motor_radius = Input(0.016786)
    motor_length = Input(0.037418)
    airfoil_prop = Input('hs522')

    @Attribute
    def p_c_root(self):
        return 0.013 * self.w_c_root / 0.4342

    @Attribute
    def p_c_tip(self):
        return self.p_c_root * self.p_taper

    @Attribute
    def p_semi_span(self):
        return 0.1 * self.w_c_root / 0.4342

    @Attribute
    def p_sweep(self):
        return degrees(atan(((self.p_c_root - self.p_c_tip) / 2) / self.p_semi_span))

    @Part
    def propeller_joint(self):
        return Cylinder(radius=(self.p_c_root + 0.001) / 2,
                        height=0.015 * self.w_c_root / 0.4342,
                        angle=pi * 2,
                        position=rotate90(translate(self.position,
                                                    "x", self.motor_length,
                                                    "z", self.motor_radius * 1.1),
                                          "y"),
                        color="gray",
                        hidden=False)

    @Part
    def propeller_blade_right(self):
        return LiftingSurface(
            w_c_root=self.p_c_root,
            w_c_tip=self.p_c_root * self.p_taper,
            airfoil_root=self.airfoil_prop,
            airfoil_tip=self.airfoil_prop,
            t_factor_root=1,
            t_factor_tip=1,
            w_semi_span=self.p_semi_span,
            sweep=self.p_sweep,
            twist=self.p_twist,
            position=rotate(translate  # longitudinal and vertically translation w.r.t. fuselage
                            (self.position,
                             "x", self.motor_length + 0.005,
                             "z", self.motor_radius * 1.1 + self.p_c_root / 2),
                            "y", radians(65)),
            mesh_deflection=0.0001,
            color="gray",
            hidden=False,
        )

    @Part
    def propeller_blade_mirrored(self):
        return MirroredShape(
            shape_in=self.propeller_blade_right,
            reference_point=translate(self.position,
                                      "x", self.motor_length + 0.009,
                                      "z", self.motor_radius * 1.1),
            vector1=self.position.Vz,
            mesh_deflection=0.0001,
            color="gray",
            hidden=True,
        )

    @Part
    def propeller_blade_left(self):
        return RotatedShape(
            shape_in=self.propeller_blade_mirrored,
            rotation_point=translate(self.position,
                                     "x", self.motor_length + 0.009,
                                     "z", self.motor_radius * 1.1),
            vector=Vector(0, 1, 0),
            angle=radians(180),
            mesh_deflection=0.0001,
            color="gray",
            hidden=False
        )

#    @Part
#    def propeller(self):
#        return Fused(
#            shape_in=self.propeller_joint,
#            tool=[self.propeller_right,
#                  self.propeller_left],
#            mesh_deflection=0.0001,
#            color="gray",
#            color="gray",
#            hidden=False
#        )


if __name__ == '__main__':
    from parapy.gui import display

    obj = Propeller()
    display(obj)
