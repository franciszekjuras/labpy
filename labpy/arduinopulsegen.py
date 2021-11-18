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

def _floatify(v, precision=8):
    if isinstance(v, int):
        return (str(v) + '.0')
    if isinstance(v, float):
        if v.is_integer():
            return str(v)
        return (f"{v:.{precision}f}".rstrip('0'))
    raise TypeError(f"Variable of type {type(v)} is not a float" )

def _to_enum(v, Type):
    if isinstance(v, str):
        return Type[v.upper().replace(' ','_')]
    return Type(v)

class ArduinoPulseGen:

    class TimeUnit(Enum):
        CYCLE, US, MS, S = 0, 1, 2, 3

    def __init__(self, rm: pyvisa.ResourceManager, name, useNiMaxSettings = True, portmap = {}):
        access_mode = 4 if useNiMaxSettings else 0
        self._res = rm.open_resource(name, access_mode=access_mode, write_termination='\n', read_termination='\n')
        self.portmap = portmap

    def _map_ch(self, ch):
        if isinstance(ch, str):
            ch = self.portmap[ch]
        return _intify(ch)

    @property
    def identity(self):
        return self._res.query("*IDN?")

    @property
    def time_unit(self):
        return self._res.query("syst:unit?")
    @time_unit.setter
    def time_unit(self, v):
        unit_str = _to_enum(v, self.TimeUnit).name.lower()
        self._res.write("syst:unit " + unit_str + ";syst:unit:store")

    def set(self, val, *chs):
        if len(chs) == 1 and not isinstance(chs[0], str):
            chs = chs[0]
        chs_str = ','.join([self._map_ch(ch) for ch in chs])
        cmd = "outp:on " if bool(val) else "outp:off "
        self._res.write(cmd + chs_str)

    def xon(self, *chs):
        if len(chs) == 1 and not isinstance(chs[0], str):
            chs = chs[0]
        chs_str = ','.join([self._map_ch(ch) for ch in chs])
        self._res.write("outp:xon " + chs_str)

    def on(self, *chs):
        self.set(True, *chs)

    def off(self, *chs):
        self.set(False, *chs)

    def add(self, ch, *pulses):
        if len(pulses) == 1 and not isinstance(pulses[0], str):
            pulses = pulses[0]
        pulses_str = ','.join([_floatify(v) for v in pulses])
        self._res.write("puls " + self._map_ch(ch) + ',' + pulses_str)

    def xadd(self, ch, *pulses):
        if len(pulses) == 1 and not isinstance(pulses[0], str):
            pulses = pulses[0]
        pulses_str = ','.join([_floatify(v) for v in pulses])
        self._res.write("puls:xadd " + self._map_ch(ch) + ',' + pulses_str)

    def reset(self, ch=None):
        if ch:
            self._res.write("puls:reset " + self._map_ch(ch))
        else:
            self._res.write("puls:reset")

    def run(self):
        self._res.write("puls:run")



if __name__ == "__main__":
    visa = pyvisa.ResourceManager()
    duo = ArduinoPulseGen(visa, "Arduino")
    # import constants
    # duo.portmap = constants.arduino.portmap
    print(duo.identity)
    duo.time_unit = "ms"
    print(duo.time_unit)
    # duo.reset()
    # duo.add("daqTrig", (0, 1.00341234))
    # duo.add("extra", (0, 2.1134312344))
    # duo._res.query("puls?")
    # duo.run()