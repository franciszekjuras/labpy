import pyvisa

class TB3000AomDriver:
    def __init__(self, rm: pyvisa.ResourceManager, dev: str, use_nimax_settings = True, **ignored):
        if use_nimax_settings:
            kwargs = {'access_mode': 4}
        else:
            kwargs = {'baud_rate': 19200}
        self._res = rm.open_resource(dev, **kwargs, write_termination='\n', read_termination='\n')

    @property
    def identity(self):
        return self._res.query("*IDN?")

    @property
    def amplitude(self):
        return float(self._res.query('AOn?'))/100
    @amplitude.setter
    def amplitude(self, v):
        v = round(min(max(v, 10.), 100.) * 10)
        self._res.write("AOn " + str(v * 10))

    def output(self, set=True):
        if bool(set):
            self._res.write("OUT_on")
        else:
            self._res.write("OUT_off")