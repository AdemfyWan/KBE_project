from parapy.core import *
from parapy.geom import *
import numpy as np
import os

DIR = os.path.dirname(__file__)


class Payload(Box):
    w_c_root = Input(0.4243)
    t_factor = Input(2)
    fu_width = Input(0.33402)
    payload_weight = Input(0.5)
    airfoil_name = Input("hs522")

    @Attribute
    def root_x_points(self):
        with open(DIR + "/Airfoils/" + self.airfoil_name + ".dat", 'r') as f:
            x = []
            for line in f:
                a, b = line.split(' ', 1)
                x.append(float(a)*self.w_c_root)
        return x

    @Attribute
    def root_z_points(self):
        with open(DIR + "/Airfoils/" + self.airfoil_name + ".dat", 'r') as f:
            z = []
            for line in f:
                a, b = line.split(' ', 1)
                z.append(float(b)*self.w_c_root*self.t_factor)
        return z

    @Input
    def height(self):  # z  # TO BE UPDATED
        half_index = self.root_x_points.index(0)
        xp = list(reversed(self.root_x_points[0:half_index]))
        fp = list(reversed(self.root_z_points[0:half_index]))
        return np.interp(self.w_c_root*0.1+0.005, xp, fp)-0.004

    @Input
    def length(self):  # y  # TO BE UPDATED
        return self.fu_width*0.75-0.01

    @Input
    def width(self):  # x   # TO BE UPDATED
        return 0.13 * self.w_c_root / 0.4342


if __name__ == '__main__':
    from parapy.gui import display

    obj = Payload()
    display(obj)
