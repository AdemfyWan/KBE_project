from math import radians, tan, sqrt
from parapy.geom import *
from parapy.core import *
from airfoil import Airfoil
from ref_frame import Frame
import numpy as np


class LiftingSurface(LoftedSolid):
    airfoil_root = Input("hs522")
    airfoil_tip = Input("hs522")

    w_c_root = Input(0.4342)
    w_c_tip = Input(0.4342*0.5)
    t_factor_root = Input(2)
    t_factor_tip = Input(1)

    w_semi_span = Input(1.0259)
    sweep = Input(25)
    twist = Input(-2)

    @Attribute
    def profiles(self):
        return [self.root_airfoil, self.tip_airfoil]

    @Attribute
    def volume_calc(self):
        area1 = self.root_airfoil.area_calc
        area2 = self.tip_airfoil.area_calc
        length = self.w_semi_span
        return length / 3 * (area1 + area2 + sqrt(area1 * area2))

    @Part
    def lifting_surf_frame(self):
        return Frame(pos=self.position,
                     hidden=True)

    @Part
    def root_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_root,
                       chord=self.w_c_root,
                       thickness_factor=self.t_factor_root,
                       mesh_deflection=0.0001)

    @Part
    def tip_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_tip,
                       chord=self.w_c_tip,
                       thickness_factor=self.t_factor_tip,
                       position=rotate(translate(self.position,
                                                 "y", self.w_semi_span,
                                                 "x", self.w_semi_span * tan(radians(self.sweep))),
                                       "y", radians(self.twist)),
                       mesh_deflection=0.0001)

 #   @Part
 #   def tip_airfoil(self):
 #       return Airfoil(airfoil_name=self.airfoil_tip,
 #                      chord=self.w_c_tip,
 #                      thickness_factor=self.t_factor_tip,
 #                      x_pos=self.w_semi_span * tan(radians(self.sweep)),
 #                      y_pos=self.w_semi_span,
 #                      mesh_deflection=0.0001)

    @Part
    def lofted_surf(self):
        return LoftedSurface(profiles=self.profiles,
                             hidden=not(__name__ == '__main__'))


if __name__ == '__main__':
    from parapy.gui import display
    obj = LiftingSurface(label="lifting surface",
                         mesh_deflection=0.0001
                         )
    display(obj)
