import pyvisa
from ..utils import floatify, intify

class KeithleyCS:
    def __init__(self, rm: pyvisa.ResourceManager, dev='KEITHLEY', **ignored):
        self._res = rm.open_resource(dev, write_termination='\n', read_termination='\n')
        self._res.write("*RST")

    @property
    def current():
        raise NotImplementedError()
    @current.setter
    def current(self, v):
        self._res.write("SOUR:CURR " + _floatify(v))

    def set_sweep(self, currents:list, trig_line:int = 1, count:int=1):
        if len(currents) == 0:
            raise ValueError(f"len(currents) should be non-zero")
        if trig_line not in range(1, 6+1):
            raise ValueError(f"trig_line ({trig_line}) is not an integer from 1 to 6")
        if not isinstance(count, int) or count < 1:
            raise ValueError(f"count ({count}) should be a positive integer")
        self._res.write("SOUR:SWE:SPAC LIST")
        self._res.write("SOUR:SWE:RANG BEST")
        self._res.write("SOUR:LIST:CURR " + ','.join([_floatify(c, 9) for c in currents]))
        self._res.write("SOUR:LIST:DEL " + ','.join(['1e-3'] * len(currents)))
        self._res.write("SOUR:LIST:COMP " + ','.join(['10'] * len(currents)))
        self._res.write("SOUR:SWE:COUN " + _intify(count))
        self._res.write("SOUR:SWE:CAB OFF")
        self._res.write("TRIG:SOUR TLIN")
        self._res.write("TRIG:ILIN " + _intify(trig_line))
        self._res.write("SOUR:SWE:ARM")

    def init(self):
        # self._res.write("SOUR:SWE:ARM")
        self._res.write("INIT")

    def set_remote_only(self, b:bool=True):
        s = "OFF" if b else "ON"
        self._res.write("DISP:ENAB " + s)

    def on(self):
        self._res.write("OUTP ON")

    def off(self):
        self._res.write("OUTP OFF")

