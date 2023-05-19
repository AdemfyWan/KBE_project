from scipy.integrate import quad
import numpy

S = 1.63
fu = 0.47
bw = 1.45
cr = 0.61
t = 0.5
ct = cr*t


def func1(y):
    return y**2


def func2(y):
    return y**3


result1 = quad(func1, 0, fu/2)
print(result1[0])

result2 = quad(func2, fu/2, bw)
print(result2[0])

mac = 2/S*(result1[0]+result2[0])
print(mac)

print("----")


xp = [0.3, 0.6]
fp = [1.45, 0]
res3 = numpy.interp(0.47, xp, fp)
print(res3)
print("test "+str(res3)+" test")


