import pyvisa
from enum import Enum
from ..utils import floatify, intify, to_enum

class ArduinoPulseGen:

    class TimeUnit(Enum):
        CYCLE, US, MS, S = 0, 1, 2, 3

    def __init__(self, rm: pyvisa.ResourceManager, dev: str, useNiMaxSettings = True,
            portmap = {}, time_unit='ms', **ignored):
        access_mode = 4 if useNiMaxSettings else 0
        self._res = rm.open_resource(dev, access_mode=access_mode, write_termination='\n', read_termination='\n')
        self.reset_full()
        self.portmap = portmap
        self.time_unit = time_unit

    def _map_ch(self, ch):
        if isinstance(ch, str):
            ch = self.portmap[ch]
        return intify(ch)

    @property
    def identity(self):
        return self._res.query("*IDN?")

    def status(self, debug: bool = False):
        com = "puls? -l" if debug else "puls?"
        return self._res.query(com)

    @property
    def time_unit(self):
        return self._res.query("syst:unit?")
    @time_unit.setter
    def time_unit(self, v):
        unit_str = to_enum(v, self.TimeUnit).name.lower()
        self._res.write("syst:unit " + unit_str)

    def time_unit_store(self):
        self._res.write("syst:unit:store")
    # def time_unit_recall(self):
    #     self._res.write("syst:unit:rec")

    def set_ch(self, val, chs):
        if isinstance(chs, (int, str)):
            chs = (chs,)
        chs_str = ','.join([self._map_ch(ch) for ch in chs])
        cmd = "outp:on " if bool(val) else "outp:off "
        self._res.write(cmd + chs_str)

    def xon(self, chs):
        if isinstance(chs, (int, str)):
            chs = (chs,)
        chs_str = ','.join([self._map_ch(ch) for ch in chs])
        self._res.write("outp:xon " + chs_str)

    def on(self, chs):
        self.set_ch(True, chs)

    def off(self, chs = ()):
        self.set_ch(False, chs)

    def _add(self, chs, pulses, ver):
        if isinstance(pulses, (float, int)):
            pulses = (pulses,)
        if len(pulses) == 0:
            return
        pulses_str = ','.join([floatify(v) for v in pulses])
        if isinstance(chs, (str, int)):
            chs = (chs,)
        for ch in chs:
            self._res.write("puls:" + ver + ' ' + self._map_ch(ch) + ',' + pulses_str)
    def add(self, chs, pulses):
        self._add(chs, pulses, ver="add")

    def xadd(self, chs, pulses):
        self._add(chs, pulses, ver="xadd")

    def reset(self, ch=None):
        if ch:
            self._res.write("puls:reset " + self._map_ch(ch))
        else:
            self._res.write("puls:reset")

    def reset_full(self):
            self._res.write("*rst")
            # self._res.write("outp:off") #Quick fix, remove after updating Duo

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