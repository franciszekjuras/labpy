import pyvisa
from typing import Union
from ..utils import check_type

class Wavemeter:

    def __init__(self, rm: pyvisa.ResourceManager, computer_name: str = "Wavemeter", port: int = 8001, **ignored):
        res_name = "::".join(("TCPIP", computer_name, str(port), "SOCKET"))
        self._res = rm.open_resource(res_name, write_termination='\n', read_termination='\n')

    @property
    def identity(self):
        return self._res.query("*IDN?")

    def _measure(self, channels: Union[int, tuple], what: str):
        if isinstance(channels, int):
            channels = (channels,)
        check_type((int), *channels)
        resp: str = self._res.query("meas:" + what + ' ' + ','.join([str(ch) for ch in channels]))
        vals = [float(v) for v in resp.split(",")]
        if len(vals) == 1:
            return vals[0]
        return vals

    def frequency(self, channels: Union[int, tuple]):
        return self._measure(channels, "freq")

    def wavelength(self, channels: Union[int, tuple]):
        return self._measure(channels, "wav")
