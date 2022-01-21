import pyvisa
from ..utils import floatify, intify, str_to_value
from ..types import IndexedProperty

unit = 1e-6

class DmtCS:
    def __init__(self, rm: pyvisa.ResourceManager, dev='DMT', use_nimax_settings=False, **ignored):
        """Initialize connection to DMT current source. Fail if connection cannot be established.
        Parameters
        ----------
        rm
            VISA resource manager, e.g. returned by `pyvisa.ResourceManager()`
        dev: str = 'DMT'
            device name or alias, as returned by `labpy.utils.list_visa_devices` or visible in NI MAX
        use_nimax_settings: bool = False
            use connection settings saved in NI MAX
        Examples
        --------
        Check connection to DMT current source (change device name if necessary):
        ```python
        import pyvisa
        rm = pyvisa.ResourceManager()
        dmt = DmtCS(rm, 'DMT')
        print(dmt.identity)
        ```
        """
        if use_nimax_settings:
            kwargs = {'access_mode': 4}
        else:
            kwargs = {'baud_rate': 115200}
        self._res = rm.open_resource(dev, write_termination='\r\n', read_termination='\r\n', **kwargs)
        self.current = IndexedProperty(self.get_current, self.set_current)
        """array_like[float]:
        Array-like property for setting and getting current (uA) in respective channel (numbered from 1)

        Examples
        --------
        Set current to 50.5 uA in channel 2:
        ```python
        dmt.curent[2] = 50.5
        ```
        Get current to restore it later:
        ```python
        old_current = dmt.current[5]
        dmt.current[5] = 42
        ...
        dmt.current[5] = old_current
        ```
        """
        self.high_range = IndexedProperty(self.get_high_range, self.set_high_range)
        """array_like[{False: 4 mA, True: 40 mA}]:
        Array-like property for setting and getting current range in respective channel (numbered from 1)

        Examples
        --------
        Set current range to high (40 mA) in all channels
        ```python
        for i in range(1, 8+1):
            dmt.high_range[i] = True
        ```
        Notes
        -----
        Current range change will take effect only after setting current in the same channel:
        ```python
        dmt.high_range[5] = False
        # Nothing yet happens
        dmt.current[5] = 20.5
        # Range and current are changed simultanously
        ```
        """
        self._high_range_cache = {k: None for k in range(1, 8+1)}

    @property
    def identity(self):
        """str: Read only property returning identify string"""
        return self._res.query("!idn")

    def set_current(self, ch, v):
        if ch not in range(1, 8+1):
            raise ValueError("Channel index must be an integer from 1 to 8")
        if isinstance(v, (list, tuple)):
            v, high_range = v
            self.high_range[ch] = high_range
        rng = '40mA' if self.high_range[ch] else '4mA'
        message = ';'.join(['!set', str(ch), rng , floatify(v, 3)])
        self._res.write(message)

    def get_current(self, ch):
        if ch not in range(1, 8+1):
            raise ValueError("Channel index must be an integer from 1 to 8")
        resp = self._res.query("!chk;" + str(ch))
        return str_to_value(resp.split(';')[3], base=unit)
        
    def set_high_range(self, ch, v):
        if ch not in range(1, 8+1):
            raise ValueError("Channel index must be an integer from 1 to 8")
        self._high_range_cache[ch] = bool(v)

    def get_high_range(self, ch):
        if ch not in range(1, 8+1):
            raise ValueError("Channel index must be an integer from 1 to 8")
        if self._high_range_cache[ch] is None:
            rng = self._res.query("!chk;" + str(ch)).split(';')[2]
            if rng == '4mA':
                self._high_range_cache[ch] = False
            elif rng == '40mA':
                self._high_range_cache[ch] = True
            else:
                raise ValueError(f"Unknown range {rng}")
        return self._high_range_cache[ch]
        