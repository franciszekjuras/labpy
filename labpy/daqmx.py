from __future__ import annotations
import PyDAQmx as dmx
import numpy as np

def _dev_path_join(*args):
    return '/' + '/'.join([arg.strip('/') for arg in args])

def _dmx_get(getter, type):
    var = type()
    getter(dmx.byref(var))
    return var.value

class Measurement:

    def __init__(self, dev: str = "Dev1", channels: str | tuple = (),  freq=1000., time=1., trig: str = None, t0 = 0.):
        self._running = False
        self._dev = dev
        self._time = time
        self._samples = int(time * freq)
        self._pre_samples = 0
        self._triggered = False
        # SetSampQuantSampPerChan(uInt64) # to change later number of samples
        self._task = dmx.Task()
        if isinstance(channels, str):
            channels = (channels,)
        chs = ','.join([_dev_path_join(dev, ch) for ch in channels])
        if not chs:
            raise ValueError("At least one channel must be specified")
        print(chs)
        # CreateAIVoltageChan(physicalChannel: str, nameToAssignToChannel: str, terminalConfig: enum, minVal: float, maxVal: float, units: enum, None);
        self._task.CreateAIVoltageChan(chs, "", dmx.DAQmx_Val_Cfg_Default, -10., 10., dmx.DAQmx_Val_Volts, None)
        # CfgSampClkTiming(source: str, rate: float, activeEdge: enum, sampleMode: enum, sampsPerChan: int);
        self._task.CfgSampClkTiming("", freq, dmx.DAQmx_Val_Rising, dmx.DAQmx_Val_FiniteSamps, self._samples)
        if trig:
            self._triggered = True
            if t0 > 0:
                return ValueError(f"t0 must be negative or zero (is {t0})")
            if t0 == 0:
                self._task.CfgDigEdgeStartTrig(_dev_path_join(dev, trig), dmx.DAQmx_Val_Rising)
            else:
                self._pre_samples = max(2, -t0 * freq)
                self._task.CfgDigEdgeRefTrig(_dev_path_join(dev, trig), dmx.DAQmx_Val_Rising, self._pre_samples)

        self._chs_n = _dmx_get(self._task.GetTaskNumChans, dmx.uInt32)
        self._freq = _dmx_get(self._task.GetSampClkRate, dmx.float64)
        self._t0 = -self._pre_samples / freq

    @property
    def freq(self):
        return self._freq
    @freq.setter
    def freq(self, v):
        raise NotImplementedError

    @property
    def t0(self):
        return self._t0
    @t0.setter
    def t0(self, v):
        raise NotImplementedError

    @property
    def time(self):
        return self._freq * self._samples
        # return self._time
    @time.setter
    def time(self, v):
        raise NotImplementedError
    # @property
    # def time_actual(self):
        # return self._freq * self._samples

    def start(self):
        if self._running:
            raise ValueError("Measurement already running. Must be read before starting again")
        self._running = True
        self._task.StartTask()

    def read(self):
        if not self._running:
            if self._triggered:
                raise ValueError("Measurement not running. Use start() before read()")
            else:
                self.start()
        data = np.zeros((self._chs_n, self._samples), dtype=np.float64)
        buf = data.ravel()
        # ReadAnalogF64(numSampsPerChan=int, timeout=float[sec], fillMode=enum, readArray=numpy.array, arraySizeInSamps=int, sampsPerChanRead=int_p, None);
        self._task.ReadAnalogF64(self._samples, 3.0, dmx.DAQmx_Val_GroupByChannel, buf, buf.size, dmx.byref(dmx.int32()), None)
        self._task.StopTask()
        return data