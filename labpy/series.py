from __future__ import annotations
import numpy as np
from math import floor, inf, isclose, ceil
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.ar_model import ar_select_order
import scipy.signal as dsp

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
    x = calc_x(y2d[0], *args)
    return [Series(y2d[i], x) for i in range(0, nrow)]

def calc_x(y: np.ndarray, x: np.ndarray | tuple | float, freq = None):
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
    return x

class Series:

    def __init__(self, y: np.ndarray, x: np.ndarray | tuple | float, freq = None):
        self._x: np.ndarray = calc_x(y, x, freq)
        self._y: np.ndarray = y

    def copy(self):
        return Series(self._y.copy(), self._x.copy())

    def copy_y(self):
        return Series(self._y.copy(), self._x)

    def decimate(self, samples: int = None, freq: float = None):
        raise NotImplementedError()

    def fft(self):
        real = np.isrealobj(self._y)
        ft = np.fft.rfft if real else np.fft.fft
        ftfreq = np.fft.rfftfreq if real else np.fft.fftfreq
        d = abs(self._x[1] - self._x[0])
        return Series(ft(self._y), ftfreq(self._x.size, d))

    def filter(self, ker):
            return Series(dsp.convolve(self._y, ker, mode='same'), self._x)

    def project(self, t0, lag=None, forward=False, taps=None, trend='n'):
        ret = self.copy_y()    
        p1, p2 = ret.split(t0)
        if forward:
            train = p1.y
            to_pred = p2.y
        else:
            train = p2.y[::-1]
            to_pred = p1.y[::-1]
        if lag is None and taps is None:
            lag = ar_select_order(train, maxlag=50, trend=trend, ic='hqic').ar_lags
            print(lag)
        elif taps is not None:
            lag = taps
        else:
            lag = int(lag * self.freq)
        fit = AutoReg(train, lags=lag, trend=trend).fit()
        print(fit.params)
        to_pred[:] = fit.model.predict(fit.params, start=train.size, end=train.size + to_pred.size -1)
        return ret

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
    
    @property
    def dx(self):
        return abs(self._x[1] - self._x[0])

    @property
    def freq(self):
        return 1./abs(self._x[1] - self._x[0])

    def apply(self, fun):
        return Series(fun(self._x), self._x)

    def slice(self, l=-inf, r=inf, rel=False):
        rng = self.range
        if rel:
            l = rng[0] + l if l >= 0. else rng[1] + l + self.dx
            r = rng[1] + self.dx + r if r <= 0. else rng[0] + r
        i0 = find_idx(l, rng)
        i1 = find_idx(r, rng)
        return Series(self._y[i0:i1], self._x[i0:i1])

    def split(self, s, rel=False):        
        rng = self.range
        if rel:
            s = rng[0] + s if s >= 0. else rng[1] + s + self.dx
        i = find_idx(s, rng)
        x, y = self._x, self._y
        return Series(y[:i], x[:i]), Series(y[i:], x[i:])

    def part(self, beg=0., end=1.):
        s = self._y.size
        r = (0., 1. , s + 1)
        i0 = min(find_idx(beg, r), s)
        i1 = min(find_idx(end, r), s)
        return Series(self._y[i0:i1], self._x[i0:i1])

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

def _gen_op(op):
    return lambda self, other : self._op_helper(other, op)
for op in ["__" + op + "__" for op 
in ["add", "sub", "mul", "truediv", "iadd", "isub", "imul", "idiv"]]:
    setattr(Series, op, _gen_op(op))

def _gen_np_apply(fun):
    return lambda self: Series(getattr(np, fun)(self._y), self._x)
for fun in ["abs", "real", "imag", "angle"]:
    setattr(Series, fun, _gen_np_apply(fun))

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