import numpy as np
from typing import Union
from math import inf, isclose, ceil

def _check_type(types, *vars):
    for v in vars:
        if not isinstance(v, types):
            raise TypeError(f"{type(v)} is not of type(s) {types}")

class Series:
    '''Series object represents ordered one-dimensional data.\n
    `y` property stores data (of any type accepted by `np.ndarray`), while `x` property stores equidistant, ascending
    ordering values (e.g. time or frequency).
    It supports `+`, `-`, `*`, `/`, `+=`, `-=`, `*=`, `/=` operators with some restrictions:
    - Series object must be left-hand side (lhs)
    - On right-hand side (rhs) either another `Series` object can be used
    or any type that is supported by underlying numpy array (eg. another numpy array or a single number)
    - If operation is performed on two `Series` objects, their x arrays must match,
    if numpy array is on rhs, its size must match with lhs `Series` object y array size

    Notes
    -----
    When new `Series` object is constructed, either explicitly with `Series()`
    or implicitly, e.g. when performing arithmetical operations or using functions
    like `slice`, `split`, only array references are copied if possible.
    Thus, if you modify x or y array in-place, changes may affect other objects.
    If you want to modify underlying arrays in-place, it's advised to make an explicit copy,
    either of both arrays with `copy` method or only of y array with `copy_y`

    See also
    --------
    `labpy.dsp`:
        collection of functions for processing data stored in `Series` object
    '''

    def __init__(self, y: np.ndarray, x: Union[np.ndarray, float] = None, freq: float = None, x0: float = 0.):
        '''Initialize Series instance. Numpy arrays passed are shallow-copied.

        Parameters
        ----------
        y: np.ndarray | Series-like
            Array with values or Series-like (with `x` and `y` attributes) object.
        x: np.ndarray | float
            Array of equidistant ordering values (e.g. time or frequency)
            or single value equal to length of measurement (e.g. total time). Exclusive with `freq` parameter.
        freq: float
            Frequency of samples. Exclusive with `x` parameter.
        x0: float
            Value added to x array when it's not passed explicitly,
            i.e. is defined by `freq` or single-valued `x` parameter. Ignored otherwise.
        '''
        if x is None and freq is None:
            # Assume x is Series-like and try to copy attributes
            x = np.asarray(y.x)
            y = np.asarray(y.y)
        self._y: np.ndarray = np.asarray(y)
        self._x: np.ndarray = Series.calc_x(self._y, x, freq, x0)

    def copy(self):
        return Series(self._y.copy(), self._x.copy())

    def copy_y(self):
        return Series(self._y.copy(), self._x)

    def decimate(self, samples: int = None, freq: float = None):
        if samples is not None and freq is not None:
            raise ValueError("Either samples or freq should be specified, not both")
        if freq is not None:
            samples = max(1, int(self.freq // freq))
        if samples is not None:
            return Series(self._y[::samples], self._x[::samples])
        else:
            raise ValueError("Either samples or freq should be specified")

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
    def span(self):
        return self._x[-1] - self._x[0] + self.dx

    @property
    def range(self):
        return self._x[0], self._x[-1], self._x.size
    
    @property
    def dx(self):
        return abs(self._x[1] - self._x[0])

    @property
    def freq(self):
        return 1./abs(self._x[1] - self._x[0])

    def apply(self, fun):
        return Series(fun(self._x), self._x)

    def slice(self, l=-inf, r=inf, rel=False):
        '''Return new `Series` object constructed by taking view of `x` array
        for values $l \\leq x < r$ and corrresponding view of `y` array.
        If `rel = False` (default), $l$ and $r$ are absolute.
        If `rel = True`, $l$ is relative to `x` array beginning if $l \\geq 0$ and end if $l < 0$,
        same for $r$ except it points to `x` array end if $r = 0$\n
        Use `cut` for default relative specification.
        '''
        rng = self.range
        if rel:
            l = rng[0] + l if l >= 0. else rng[1] + l + self.dx
            r = rng[1] + self.dx + r if r <= 0. else rng[0] + r
        i0 = Series.find_idx(l, rng)
        i1 = Series.find_idx(r, rng)
        return Series(self._y[i0:i1], self._x[i0:i1])

    def cut(self, l=-inf, r=inf):
        '''Same as `slice` with `rel = True`'''
        return self.slice(l, r, rel=True)

    def extend(self, l=None, r=None, rel=False):
        rng = self.range
        s = rng[2]
        l0, r0 = rng[0], rng[1] + self.dx
        if l is not None:
            if rel: l = l0 + l
            li = min(Series.find_idx(l, rng, norm=False), 0)
            lx = np.linspace(l0 + li * (r0 - l0) / s, l0, -li, endpoint=False)
        else: lx = np.array([])
        if r is not None:
            if rel: r = r0 + r
            ri = max(Series.find_idx(r, rng, norm=False), s)
            rx = np.linspace(r0, r0 + (ri - s) * (r0 - l0) / s, (ri - s), endpoint=False)
        else: rx = np.array([])
        return Series(
            np.concatenate([np.zeros_like(lx), self._y, np.zeros_like(rx)]),
            np.concatenate([lx, self._x, rx])
        )

    def split(self, s, rel=False):        
        rng = self.range
        if rel:
            s = rng[0] + s if s >= 0. else rng[1] + s + self.dx
        i = Series.find_idx(s, rng)
        x, y = self._x, self._y
        return Series(y[:i], x[:i]), Series(y[i:], x[i:])

    def part(self, beg=0., end=1.):
        s = self._y.size
        r = (0., 1. , s + 1)
        i0 = min(Series.find_idx(beg, r), s)
        i1 = min(Series.find_idx(end, r), s)
        return Series(self._y[i0:i1], self._x[i0:i1])

    def index(self, v):
        '''Find index corresponding to `v` in `x` array,
        i.e. translate ordering value (like time) to index in underlying arrays'''
        return Series.find_idx(v, self.range)

    def __repr__(self):
        return f"D = {self.range} y = {self._y}"

    def _op_helper(self, other, op):
        if isinstance(other, Series):
            if(self.range != other.range):
                raise ValueError(f"Series' ranges should be equal, are {self.range} and {other.range}")
            other = other.y
        if op.startswith('__i'):
            self.y = getattr(self._y, op)(other)
            return self
        else:
            return Series(getattr(self._y, op)(other), self._x)

    @staticmethod
    def find_idx(v, range, norm=True):
        l, r, s = range
        if norm:
            if v <= l or isclose(v, l):
                return 0
            if v > r and not isclose(v, r):
                return s
        i: float = (v - l)/(r - l) * (s - 1)
        if isclose(i, round(i)):
            return int(i)
        return ceil(i)

    @staticmethod
    def from2darray(y2d: np.ndarray, *args, **kwargs):
        if(y2d.ndim != 2):
            raise ValueError("y2d array should be two-dimensional")
        nrow = y2d.shape[0]
        x = Series.calc_x(y2d[0], *args, **kwargs)
        return [Series(y2d[i], x) for i in range(0, nrow)]

    @staticmethod
    def calc_x(y: np.ndarray, x: Union[np.ndarray, float] = None, freq=None, x0 = 0.):
        _check_type(np.ndarray, y)
        if y.ndim != 1:
            raise ValueError(f"Array y (dim={y.ndim}), should be one-dimensional")
        if x is not None and freq is not None:
            raise ValueError("Either x or freq should be specified, not both")
        if x is None and freq is None:
            raise ValueError("Either x or freq should be specified")
        if freq is not None:
            x = y.size / freq
        if isinstance(x, (float, int)):
            l, r = x0, x0 + x
            x = np.linspace(l, r, y.size, endpoint=False)
        else:
            x = np.asarray(x)
            if x.ndim != 1:
                raise ValueError(f"Array x (dim={x.ndim}), should be one-dimensional")
            if(x.size != y.size):
                raise ValueError(f"Array x size = {x.size} should be equal to array y size = {y.size}")
        return x

def _gen_op(op):
    return lambda self, other : self._op_helper(other, op)
for op in ["__" + op + "__" for op 
in ["add", "sub", "mul", "truediv", "iadd", "isub", "imul", "idiv"]]:
    setattr(Series, op, _gen_op(op))

def _gen_np_apply(fun):
    return lambda self: Series(getattr(np, fun)(self._y), self._x)
for fun in ["abs", "real", "imag", "angle"]:
    setattr(Series, fun, _gen_np_apply(fun))
