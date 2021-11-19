import numpy as np
from math import floor, inf, isclose, ceil

def _check_type(types, *vars):
    for v in vars:
        if not isinstance(v, types):
            raise TypeError(f"{type(v)} is not of type(s) {types}")

def find_idx(v, range):
    l, r, s = range
    if v <= l or isclose(v, l):
        return 0
    if v > r and not isclose(v, r):
        return s
    i: float = (v - l)/(r - l) * (s - 1)
    if isclose(i, round(i)):
        return int(i)
    return ceil(i)

class Series:

    def __init__(self, y: np.ndarray, x: np.ndarray):
        _check_type(np.ndarray, y)
        if not isinstance(x, np.ndarray):
            l, r = x
            x = np.linspace(l, r, y.size, endpoint=False)
        if x.ndim != 1 or y.ndim != 1:
            raise ValueError(f"Arrays x (dim={x.ndim}), y (dim={y.ndim}) should be one-dimensional")
        if(x.size != y.size):
            raise ValueError(f"Arrays x (size={x.size}), y (size={y.size}) should be of equal size")
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    @property
    def range(self):
        return self._x[0], self._x[-1], self._x.size

    def slice(self, x0=-inf, x1=inf):
        r = self.range
        i0 = find_idx(x0, r)
        i1 = find_idx(x1, r)
        xn = self._x[i0:i1]
        yn = self._y[i0:i1]
        return Series(yn, xn)

    def __repr__(self):
        r = self.range
        return f"x = {self._x}\n"\
            f"y = {self._y}"

if __name__ == "__main__":
    y = np.linspace(0.,10.,20)**2
    a = Series(y, (0, 1))
    print(a)
    # print(a.y)
    # print(a.x)
    print(a.slice(0, 0.12))
    print(a.slice(0, 0.15))
    print(a.slice(0, 0.1501))
    print(a.slice(0.9, 1))
