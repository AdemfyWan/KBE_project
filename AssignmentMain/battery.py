from parapy.core import *
from parapy.geom import *


class Battery(Box):
    endurance = Input(60)     # [min]
    v_cruise = Input(15)     # [m/s]
    cd = Input(0.0106)
    ref_area = Input(0.95822)  # [m^2]
    energy_density = Input(277)  # [Wh/L]
    specific_energy = Input(141)  # [Wh/kg]
    air_density = Input(1.1911)  # [kg/m^3]
    k1 = Input(0.38)  # width/length ratio
    k2 = Input(0.25)  # height/length ratio
    prop_eff = Input(0.70)  #
    motor_eff = Input(0.70)  #
    w_c_root = Input(0.4243)

    @Attribute
    def power(self):  # power = drag force * v_cruise
        if self.cd == 0:
            return 0
        else:
            return 0.5*self.air_density * self.v_cruise**3 * self.ref_area * self.cd / self.prop_eff / self.motor_eff

    @Attribute
    def battery_capacity(self):
        return self.power * self.endurance/60

    @Attribute
    def battery_weight(self):  # kg
        return self.battery_capacity / self.specific_energy

    @Attribute
    def battery_volume(self):   # [m^3]
        return self.battery_capacity / self.energy_density / 1000

    @Input
    def length(self):  # y
        if self.battery_volume == 0:
            return 0.10274 * self.w_c_root / 0.4342
        else:
            return (self.battery_volume/(self.k1*self.k2))**(1/3)

    @Input
    def width(self):  # x
        return self.length*self.k1

    @Input
    def height(self):  # z
        return self.length*self.k2


if __name__ == '__main__':
    from parapy.gui import display

    obj = Battery()
    display(obj)
