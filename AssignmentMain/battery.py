from parapy.core import *
from parapy.geom import *


class Battery(Box):
    w_c_root = Input(0.4243)
    payload_weight = Input(0.5)

    @Input
    def height(self):  # z  # TO BE UPDATED
        return 0.026 * self.w_c_root/0.4342

    @Input
    def length(self):  # y  # TO BE UPDATED
        return 0.139 * self.w_c_root / 0.4342

    @Input
    def width(self):  # x   # TO BE UPDATED
        return 0.047 * self.w_c_root / 0.4342

    @Attribute
    def battery_weight(self):  # TO BE UPDATED
        return self.payload_weight*2


if __name__ == '__main__':
    from parapy.gui import display

    obj = Battery()
    display(obj)
