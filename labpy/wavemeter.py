from __future__ import annotations
import pyvisa

def _check_type(types, *vars):
    for v in vars:
        if not isinstance(v, types):
            raise TypeError(f"{type(v)} is not of type(s) {types}")

class Wavemeter:

    def __init__(self, rm: pyvisa.ResourceManager, computer_name: str = "DESKTOP-HPSND6H", port: int = 8001):
        self._res = rm.open_resource("::".join(("TCPIP", computer_name, str(port), "SOCKET")), write_termination='\n', read_termination='\n')

    @property
    def identity(self):
        return self._res.query("*IDN?")

    def _measure(self, channels: int | tuple, what: str):
        if isinstance(channels, int):
            channels = (channels,)
        _check_type((int), *channels)
        resp: str = self._res.query("meas:" + what + ' ' + ','.join([str(ch) for ch in channels]))
        vals = [float(v) for v in resp.split(",")]
        if len(vals) == 1:
            return vals[0]
        return vals

    def frequency(self, channels: int | tuple):
        return self._measure(channels, "freq")

    def wavelength(self, channels: int | tuple):
        return self._measure(channels, "wav")
