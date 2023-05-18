
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

from parapy.geom import *
from parapy.core import *
from ref_frame import Frame


class Airfoil(FittedCurve):  # note the use of FittedCurve as superclass
    chord = Input(1.)
    airfoil_name = Input("hs522")
    thickness_factor = Input(1.)
    mesh_deflection = Input(0.0001)

    @Attribute
    def points(self):  # required input to the FittedCurve superclass
        with open(self.airfoil_name + ".dat", 'r') as f:
            point_lst = []
            for line in f:
                x, z = line.split(' ', 1)  # the cartesian coordinates are directly interpreted as X and Z coordinates
                point_lst.append(self.position.translate(
                   "x", float(x)*self.chord,  # the x points are scaled according to the airfoil chord length
                   "z", float(z)*self.chord*self.thickness_factor)) # the y points are scaled according to the /
                # thickness factor
        return point_lst

    @Part
    def airfoil_frame(self):  # to visualize the given airfoil reference frame
        return Frame(pos=self.position,
                     hidden=True)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Airfoil(label="airfoil")
    display(obj)