from parapy.core import *
from parapy.geom import *


class Payload(Box):
    w_c_root = Input(0.4243)
    payload_weight = Input(0.5)

    @Input
    def height(self):  # z  # TO BE UPDATED
        return 0.04 * self.w_c_root/0.4342

    @Input
    def length(self):  # y  # TO BE UPDATED
        return 0.17 * self.w_c_root / 0.4342

    @Input
    def width(self):  # x   # TO BE UPDATED
        return 0.13 * self.w_c_root / 0.4342


if __name__ == '__main__':
    from parapy.gui import display

    obj = Payload()
    display(obj)
