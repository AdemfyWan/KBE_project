from parapy.core import *
from parapy.geom import *


class Battery(Box):
    w_c_root = Input(0.4243)
    payload_weight = Input(0.5)
    Endurance = Input(60)     #[min]
    V_cruise = Input(15)     #[m/s]
    Cd = Input(0.0106)
    ref_area = Input(0.95822)  #[m^2]
    Energy_density = Input(500) #[Wh/L]
    Specific_energy = Input(200)  #[Wh/kg]
    air_density = Input(1.1911)  #[kg/m^3]


    @Input
    def height(self):  # z  # TO BE UPDATED
        return self.battery_volume/self.length/self.width

    @Input
    def length(self):  # y  # TO BE UPDATED
        return 0.12 * self.w_c_root / 0.4342

    @Input
    def width(self):  # x   # TO BE UPDATED
        return 0.047 * self.w_c_root / 0.4342

    @Attribute
    def battery_weight(self):  # TO BE UPDATED
        return 0.5*self.air_density * self.V_cruise**3 * self.ref_area * self.Cd * self.Endurance/60 / self.Specific_energy

    @Attribute
    def battery_volume(self):   # [m^3]
        return 0.5*self.air_density * self.V_cruise**3 * self.ref_area * self.Cd * self.Endurance/60 / self.Energy_density / 1000


if __name__ == '__main__':
    from parapy.gui import display

    obj = Battery()
    display(obj)
