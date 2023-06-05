from parapy.geom import *
from parapy.core import *
from ref_frame import Frame
import numpy as np
import os
from math import tan, radians


def polyarea(x_in, y_in):
    return 0.5*np.abs(np.dot(x_in, np.roll(y_in, 1))-np.dot(y_in, np.roll(x_in, 1)))


DIR = os.path.dirname(__file__)


class Airfoil(GeomBase):
    chord = Input(0.4342)
    airfoil_name = Input("hs522")
    thickness_factor = Input(2)
    twist = Input(0)
    # mesh_deflection = Input(0.0001)
    # x_pos = Input(0)
    # y_pos = Input(0)

    @Attribute
    def points(self):
        with open(DIR + "/Airfoils/" + self.airfoil_name + ".dat", 'r') as f:
            point_lst = []
            for line in f:
                x, z = line.split(' ', 1)
                point_lst.append(self.position.translate(
                   "x", float(x),
                   "z", float(z)*self.thickness_factor))
        return point_lst

    @Attribute
    def x_points(self):
        with open(DIR + "/Airfoils/" + self.airfoil_name + ".dat", 'r') as f:
            x = []
            for line in f:
                a, b = line.split(' ', 1)
                x.append(float(a)*self.chord)
        return x

    @Attribute
    def z_points(self):
        with open(DIR + "/Airfoils/" + self.airfoil_name + ".dat", 'r') as f:
            z = []
            for line in f:
                a, b = line.split(' ', 1)
                z.append(float(b)*self.chord*self.thickness_factor)
        return z

    @Part
    def airfoil_frame(self):
        return Frame(pos=self.position,
                     hidden=False)

    @Part
    def airfoil_unscaled(self):
        return FittedCurve(points=self.points,
                           color="red",
                           hidden=False)

    @Part
    def airfoil_scaled(self):
        return ScaledCurve(curve_in=self.airfoil_unscaled,
                           reference_point=self.position,
                           factor=self.chord,
                           color='yellow',
                           hidden=False)

    @Part
    def airfoil(self):
        return RotatedCurve(curve_in=self.airfoil_scaled,
                            rotation_point=self.position,
                            vector=Vector(0, 1, 0),
                            angle=radians(self.twist))


if __name__ == '__main__':
    from parapy.gui import display
    obj = Airfoil(label="airfoil")
    display(obj)
