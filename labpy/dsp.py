from .series import Series
import numpy as np
from scipy import signal

def fft(ser, pad = 1):
        real = np.isrealobj(ser._y)
        ft = np.fft.rfft if real else np.fft.fft
        ftfreq = np.fft.rfftfreq if real else np.fft.fftfreq
        d = abs(ser._x[1] - ser._x[0])
        if pad < 1.:
            raise ValueError(f"Padding should be >= 1, is {pad}")
        n = int(ser._x.size * pad)
        return Series(ft(ser._y, n=n), ftfreq(n, d))

def filter(ser, ker):
        return Series(signal.convolve(ser._y, ker, mode='same'), ser._x)

def project(ser, t0, lag=None, forward=False, taps=None, trend='c', info={}):
    try:
        from statsmodels.tsa.ar_model import AutoReg
        from statsmodels.tsa.ar_model import ar_select_order
    except ImportError as e:
        print(e)
        print("Install statsmodels manually or install labpython with [full] option e.g. pip install labpython[full]")
    ret = ser.copy_y()
    p1, p2 = ret.split(t0)
    if forward:
        train = p1.y
        to_pred = p2.y
    else:
        train = p2.y[::-1]
        to_pred = p1.y[::-1]
    if lag is None and taps is None:
        lag = ar_select_order(train, maxlag=50, trend=trend).ar_lags
    elif taps is not None:
        lag = taps
    else:
        lag = int(lag * ser.freq)
    info['lag'] = lag
    fit = AutoReg(train, lags=lag, trend=trend).fit()
    info['params'] = fit.params
    to_pred[:] = fit.model.predict(fit.params, start=train.size, end=train.size + to_pred.size -1)
    return ret
