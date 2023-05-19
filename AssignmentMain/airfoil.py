from parapy.geom import *
from parapy.core import *
from ref_frame import Frame
import os

DIR = os.path.dirname(__file__)


class Airfoil(FittedCurve):
    chord = Input(1.)
    airfoil_name = Input("hs522")
    thickness_factor = Input(1.)
    mesh_deflection = Input(0.0001)

    @Attribute
    def points(self):
        with open(DIR + "/Airfoils/" + self.airfoil_name + ".dat", 'r') as f:
            point_lst = []
            for line in f:
                x, z = line.split(' ', 1)
                point_lst.append(self.position.translate(
                   "x", float(x)*self.chord,
                   "z", float(z)*self.chord*self.thickness_factor))
        return point_lst

    @Part
    def airfoil_frame(self):
        return Frame(pos=self.position,
                     hidden=True)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Airfoil(label="airfoil")
    display(obj)
