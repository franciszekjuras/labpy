import numpy as np
from math import floor, inf, isclose, ceil

def _check_type(types, vars):
    for v in vars:
        if not isinstance(v, types):
            raise TypeError(f"{type(v)} is not of type(s) {types}")

def find_idx(v, range):
    l, r, s = range
    if v <= l:
        return 0
    if v >= r:
        return s
    i: float = (v - l)/(r - l) * s
    if isclose(i, round(i)):
        return int(i)
    return ceil(i)

class Series:

    def __init__(self, y: np.ndarray, x: np.ndarray):
        if not isinstance(x, np.ndarray):
            x = np.linspace(*x, endpoint=True)
        _check_type(np.ndarray, x, y)
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

if __name__ == "__main__":
    range = (0., 2., 2)
    print(-inf, find_idx(-inf, range))
    print(-0.1, find_idx(-0.1, range))
    print(0.0, find_idx(0.0, range))
    print(0.1, find_idx(0.1, range))
    print(1., find_idx(1., range))
    print(1.9, find_idx(1.9, range))
    print(2.0, find_idx(2.0, range))
    print(2.1, find_idx(2.1, range))
    print(inf, find_idx(inf, range))