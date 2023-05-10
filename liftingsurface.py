#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 ParaPy Holding B.V.
#
# This file is subject to the terms and conditions defined in
# the license agreement that you have received with this source code
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR
# PURPOSE.

from math import radians, tan
from parapy.geom import *
from parapy.core import *
from airfoil import Airfoil  # note this is a different class than n exe_17_wing.py
from ref_frame import Frame


class LiftingSurface(LoftedSolid):  # note use of loftedSolid as superclass
    airfoil_root = Input("whitcomb")
    airfoil_tip = Input("simm_airfoil")  #: :type: string

    w_c_root = Input(6.)
    w_c_tip = Input(2.3)
    t_factor_root = Input(1.)
    t_factor_tip = Input(1.)

    w_semi_span = Input(10.)
    sweep = Input(20)
    twist = Input(-5)

    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil, self.tip_airfoil]

    @Part
    def lifting_surf_frame(self):  # to visualize the given lifting surface reference frame
        return Frame(pos=self.position,
                     hidden=False)

    @Part
    def root_airfoil(self):  # root airfoil will receive self.position as default
        return Airfoil(airfoil_name=self.airfoil_root,
                       chord=self.w_c_root,
                       thickness_factor=self.t_factor_root,
                       mesh_deflection=0.0001)

    @Part
    def tip_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_tip,
                       chord=self.w_c_tip,
                       thickness_factor=self.t_factor_tip,
                       position=translate(
                           rotate(self.position, "y", radians(self.twist)),  # apply twist angle
                           "y", self.w_semi_span,
                           "x", self.w_semi_span * tan(radians(self.sweep))),  # apply sweep
                       mesh_deflection=0.0001)

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
