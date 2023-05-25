
import os
import numpy as np
import matplotlib.pyplot as plt
from math import tan, radians

xp = [4, 3, 2, 1]
fp = [1, 1, 2, 2]

cp = np.interp(2.5, xp, fp)

print(cp)

print(list(reversed(xp)))

print(max(0,0))