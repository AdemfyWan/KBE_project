from parapy.core import *
from parapy.geom import *
from math import pi
from propeller import Propeller
from ref_frame import Frame


class MotorAssembly(GeomBase):
    w_c_root = Input(0.4243)
    airfoil_prop = Input('hs522')
    power_weight_ratio = Input(220)
    mtow = Input(2.4396)

    specific_power = Input(4829)  # benchmark specific power: 4,829 W/kg
    power_density = Input(16204375)  # benchmark power density: 16,204,371 W/m3

    @Attribute  # TO BE UPDATED
    def motor_power(self):
        return self.power_weight_ratio*self.mtow

    @Attribute  # TO BE UPDATED
    def motor_weight(self):
        return self.motor_power/self.specific_power  # benchmark power weight density: 4,716 W/kg

    @Attribute  # TO BE UPDATED
    def motor_volume(self):
        return self.motor_power/self.power_density  # benchmark power volume density: 16,204,375 W/m3

    @Attribute  # TO BE UPDATED
    def motor_diameter(self):
        return (self.motor_volume*4/(pi*1.1146))**(1/3)  # benchmark length/diameter ratio: 1.1146

    @Attribute  # TO BE UPDATED
    def motor_radius(self):
        return self.motor_diameter/2

    @Attribute  # TO BE UPDATED
    def motor_length(self):
        return self.motor_diameter*1.1146

    @Part
    def motor_assembly_frame(self):
        return Frame(pos=self.position,
                     hidden=True)

    @Part
    def motor(self):
        return Cylinder(
            radius=self.motor_radius,
            height=self.motor_length,
            angle=pi*2,
            position=rotate90(translate(self.position,
                                        'z', self.motor_radius * 1.1),
                              'y'),
            color="gray"
        )

    @Part
    def propeller(self):
        return Propeller(
            w_c_root=self.w_c_root,
            motor_radius=self.motor_radius,
            motor_length=self.motor_length,
            airfoil_prop=self.airfoil_prop,
        )


if __name__ == '__main__':
    from parapy.gui import display

    obj = MotorAssembly()
    display(obj)
