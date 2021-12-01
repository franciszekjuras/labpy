import pyvisa
from enum import Enum

def _intify(v):
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        else:
            raise ValueError(f"{v} is not an exact integer")
    raise TypeError(f"Variable of type {type(v)} is not an integer" )

def _floatify(v, precision=6):
    if isinstance(v, int):
        return (str(v) + '.0')
    if isinstance(v, float):
        if v.is_integer():
            return str(v)
        return (f"{v:.{precision}f}".rstrip('0'))
    raise TypeError(f"Variable of type {type(v)} is not a float" )

def _to_enum(v, Type):
    # if isinstance(v, int):
    #     v = Type(v)
    if isinstance(v, str):
        return Type[v.upper().replace(' ','_')]
    return Type(v)

class Srs:

    class Trigger(Enum):
        SINE_ZERO = 0
        RISING = 1
        FALLING = 2

    class Source(Enum):
        EXTERNAL = 0
        INTERNAL = 1

    class Reserve(Enum):
        HIGH_RESERVE = 0
        NORMAL = 1
        LOW_NOISE = 2

    class Input(Enum):
        X, Y, R, TH = 1, 2, 3, 4
        AUX1, AUX2, AUX3, AUX4 = 5, 6, 7, 8
        FREQ, DISP1, DISP2 = 9, 10, 11

    Sensitivity = {
        "2 nV": 0, "5 nV": 1, "10 nV": 2, "20 nV": 3, "50 nV": 4, "100 nV": 5,
        "200 nV": 6, "500 nV": 7, "1 uV": 8, "2 uV": 9, "5 uV": 10, "10 uV": 11,
        "20 uV": 12, "50 uV": 13, "100 uV": 14, "200 uV": 15, "500 uV": 16, "1 mV": 17,
        "2 mV": 18, "5 mV": 19, "10 mV": 20, "20 mV": 21,"50 mV": 22, "100 mV": 23,
        "200 mV": 24, "500 mV": 25, "1 V": 26,
    }
    SensitivityInv = {v: k for k, v in Sensitivity.items()}

    TimeConstant = {
        "10 us": 0, "30 us": 1, "100 us": 2, "300 us": 3, "1 ms": 4, "3 ms": 5,
        "10 ms": 6, "30 ms": 7, "100 ms": 8, "300 ms": 9, "1 s": 10, "3 s": 11,
        "10 s": 12, "30 s": 13, "100 s": 14, "300 s": 15, "1 ks": 16, "3 ks": 17,
        "10 ks": 18, "30 ks": 19,
    }
    TimeConstantInv = {v: k for k, v in TimeConstant.items()}

    FilterSlope = {
        "6 dB/oct": 0, "12 dB/oct": 1, "18 dB/oct": 2, "24 dB/oct": 3,
    }
    FilterSlopeInv = {v: k for k, v in FilterSlope.items()}


    def __init__(self, rm: pyvisa.ResourceManager, name: str, auxout_map = {}, auxin_map = {}):
        self._res = rm.open_resource(name, write_termination='\n', read_termination='\n')
        self.auxout_map = auxout_map
        self.auxin_map = auxin_map

    def setup(self, attrs: dict):
        for key, value in attrs.items():
            setattr(self, key, value)

    @property
    def identity(self):
        return self._res.query("*IDN?")

    @property
    def source(self):
        return self.Source(int(self._res.query("FMOD?"))).name
    @source.setter
    def source(self, v: Source):
        self._res.write("FMOD " + str(_to_enum(v, self.Source).value))

    @property
    def reserve(self):
        return self.Reserve(int(self._res.query("RMOD?"))).name
    @reserve.setter
    def reserve(self, v: Reserve):
        self._res.write("RMOD " + str(_to_enum(v, self.Reserve).value))

    @property
    def frequency(self):
        return float(self._res.query("FREQ?"))
    @frequency.setter
    def frequency(self, v):
        self._res.write("FREQ " + _floatify(v))

    @property
    def phase(self):
        return float(self._res.query("PHAS?"))
    @phase.setter
    def phase(self, v):
        if not -360. <= v < 730:
            raise ValueError(f"Phase value {v} is not in range [-360, 730)")
        self._res.write("PHAS " + _floatify(v))

    @property
    def harmonic(self):
        return int(self._res.query("HARM?"))
    @harmonic.setter
    def harmonic(self, v):
        if not int(v) in range(1, 20000):
            raise ValueError(f"Harmonic value {v} is not in range [1, 19999]")
        self._res.write("HARM " + _intify(v))

    @property
    def sensitivity(self):
        return self.SensitivityInv[int(self._res.query("SENS?"))]
    @sensitivity.setter
    def sensitivity(self, v):
        self._res.write("SENS " + str(self.Sensitivity[v]))

    @property
    def time_constant(self):
        return self.TimeConstantInv[int(self._res.query("OFLT?"))]
    @time_constant.setter
    def time_constant(self, v):
        self._res.write("OFLT " + str(self.TimeConstant[v]))

    @property
    def filter_slope(self):
        return self.FilterSlopeInv[int(self._res.query("OFSL?"))]
    @filter_slope.setter
    def filter_slope(self, v):
        self._res.write("OFSL " + str(self.FilterSlope[v]))

    def snap(self, params):
        if not len(params) in range (2, 6+1):
            raise ValueError(f"Min. 2, max. 6 values can be snapped at once (not {len(params)})")
        params_str = [str(_to_enum(p, self.Input).value) for p in params]
        res = self._res.query("SNAP? " + ','.join(params_str))
        return [float(v) for v in res.split(',')]

    def demod(self, param):
        e = _to_enum(param, self.Input)
        if e.value not in range(1, 4+1):
            raise ValueError(f"{e.name} is not a demodulated channel")
        return self._res.query("OUTP? " + str(e.value))

    def auxin(self, num):
        if isinstance(num, str):
            num = self.auxin_map[num]
        if not isinstance(num, int) or not num in range(1, 4+1):
            raise ValueError(f"{num} is not an integer from 1 to 4")
        return self._res.query("OAUX? " + str(num))

    def auxout(self, num: int, value: float = None):
        if isinstance(num, str):
            num = self.auxout_map[num]     
        if not isinstance(num, int) or not num in range(1, 4+1):
            raise ValueError(f"{num} is not an integer from 1 to 4")
        if value is None:
            return self._res.query("AUXV? " + str(num))
        else:
            self._res.write("AUXV " + str(num) + ',' + _floatify(value, 3))

    @property
    def x(self):
        return self.demod(self.Input.X)
    @property
    def y(self):
        return self.demod(self.Input.Y)
    @property
    def r(self):
        return self.demod(self.Input.R)
    @property
    def th(self):
        return self.demod(self.Input.TH)
    @property
    def xy(self):
        return self.snap('x','y')
    @property
    def rth(self):
        return self.snap(('r','th'))

if __name__ == "__main__":

    visa = pyvisa.ResourceManager()
    lockin = Srs(visa.open_resource('Lock-in', write_termination='\n', read_termination='\n'))
    print(lockin.identity)
    lockin.source = Srs.Source.INTERNAL
    lockin.reserve = Srs.Reserve.NORMAL
    lockin.frequency = 500.16
    setattr(lockin, "frequency", 512.)
    lockin.phase = 0
    lockin.harmonic = 1
    lockin.sensitivity = "5 mV"
    lockin.time_constant = "1 ms"
    lockin.filter_slope = "12 dB/oct"
    print(lockin.source)
    print(lockin.reserve)
    print(lockin.frequency)
    print(lockin.phase)
    print(lockin.harmonic)
    print(lockin.sensitivity)
    print(lockin.time_constant)
    print(lockin.filter_slope)
    print(lockin.demod('x'))
    print(lockin.x)
    print(lockin.snap('x', 'y'))
    In = Srs.Input
    print(lockin.snap(In.AUX3, In.X, In.Y))
    print(lockin.snap(('x', 'y')))
    print(lockin.aux(1))
    print(lockin.xy)
    print(lockin.rth)
