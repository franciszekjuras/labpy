from __future__ import annotations
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

def from2darray(y2d: np.ndarray, *args):
    if(y2d.ndim != 2):
        raise ValueError("y2d array should be two-dimensional")
    nrow = y2d.shape[0]
    x = Series(y2d[0], *args).x
    return [Series(y2d[i], x) for i in range(0, nrow)]


class Series:

    def __init__(self, y: np.ndarray, x: np.ndarray | tuple | float, freq = None):
        _check_type(np.ndarray, y)
        if not isinstance(x, np.ndarray):
            if freq:
                l, r = x, x + (y.size / freq)
            else:
                l, r = x
            x = np.linspace(l, r, y.size, endpoint=False)
        if x.ndim != 1 or y.ndim != 1:
            raise ValueError(f"Arrays x (dim={x.ndim}), y (dim={y.ndim}) should be one-dimensional")
        if(x.size != y.size):
            raise ValueError(f"Arrays x (size={x.size}), y (size={y.size}) should be of equal size")
        self._x: np.ndarray = x
        self._y: np.ndarray = y

    def copy(self):
        return Series(self._y.copy(), self._x.copy())

    def copy_y(self):
        return Series(self._y.copy(), self._x)

    def decimate(self, samples: int = None, freq: float = None):
        raise NotImplementedError()

    @property
    def xy(self):
        return (self._x, self._y)

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, x: np.ndarray):
        _check_type(np.ndarray, x)
        if(x.shape != self._y.shape):
            raise ValueError(f"Array x (shape={x.shape}) should be of the same shape as y (shape={self._y.shape})")
        self._x = x

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, y: np.ndarray):
        _check_type(np.ndarray, y)
        if(y.shape != self._x.shape):
            raise ValueError(f"Array y (shape={y.shape}) should be of the same shape as x (shape={self._x.shape})")
        self._y = y

    @property
    def range(self):
        return self._x[0], self._x[-1], self._x.size

    def slice(self, x0=-inf, x1=inf):
        r = self.range
        i0 = find_idx(x0, r)
        i1 = find_idx(x1, r)
        return Series(self._y[i0:i1], self._x[i0:i1])

    def part(self, beg=0., end=1.):
        s = self._y.size
        r = (0., 1. , s + 1)
        i0 = min(find_idx(beg, r), s)
        i1 = min(find_idx(end, r), s)
        return Series(self._y[i0:i1], self._x[i0:i1])

    def __repr__(self):
        return f"x = {self._x}\n"\
            f"y = {self._y}"

def _assignop_helper(inst, other, op):
    inst.y = getattr(inst.y, op)(other)
    return inst
for op in ["__" + op + "__" for op in ["add", "sub", "mul", "truediv"]]:
    setattr(Series, op, lambda self, other, c_op=op : Series(getattr(self.y, c_op)(other), self.x))
for op in ["__" + op + "__" for op in ["iadd", "isub", "imul", "idiv"]]:
    setattr(Series, op, lambda self, other, c_op=op : _assignop_helper(self, other, c_op))

class Average:

    def __init__(self, v = None):
        if v is not None:
            self.sum = v * 1.
        self.count = 0 if v is None else 1

    def add(self, v):
        if self.count == 0:
            self.sum = v * 1.
        else:
            self.sum += v
        self.count += 1

    @property
    def value(self):
        if self.count == 0:
            return 0.
        return self.sum / self.count