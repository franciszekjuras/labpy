import sys
import os
import ctypes
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from labpy.server import Server
from labpy.scpi_parser import ScpiParser

lib = ctypes.windll.wlmData

lib.GetWavelengthNum.restype = ctypes.c_double
lib.GetWavelengthNum.argtypes = [ctypes.c_long, ctypes.c_double]

lib.GetFrequencyNum.restype = ctypes.c_double
lib.GetFrequencyNum.argtypes = [ctypes.c_long, ctypes.c_double]

def identify(args):
    return "LabPy,Wavemeter,NA,v21.11a"

# def get_wavelength(ch):
#     if ch not in range(1, 8 + 1):
#         return 0.
#     wav = lib.GetWavelengthNum(ch)
#     if(wav < 0):
#         return 0.
#     return wav

# def get_wavelength(ch):
#     if ch not in range(1, 8 + 1):
#         return 0.
#     wav = lib.GetWavelengthNum(ch)
#     if(wav < 0):
#         return 0.
#     return wav

def sanitize_channels(args):
    channels = []
    for arg in args:
        try:
            i = int(arg)
            if i in range(1, 8 + 1):
                channels.append(i)
            else:
                channels.append(None)
        except ValueError:
            channels.append(None)
    return channels

def measure(args, fun):
    channels = sanitize_channels(args)
    meas = [fun(ch, 0.) if ch else 0. for ch in channels]
    meas_san = [v if v > 0. else 0. for v in meas]
    return meas_san

def measure_wavelength(args):
    return measure(args, fun=lib.GetWavelengthNum)
    
def measure_frequency(args):
    return measure(args, fun=lib.GetFrequencyNum)

# def measure_wavelegnth(args):
#     res = []
#     for i_s in args:
#         try:
#             i = int(i_s)
#             if(i >= 0 and i <= 8):
#                 res.append(get_wavelength(i))
#         except ValueError:
#             pass
#     return ','.join(res)

if(__name__ == "__main__"):

    if (len(sys.argv) > 1 and sys.argv[1] in ["--test", "-t"]):
        print(measure_wavelength(["1", "2", "3", "bubel"]))
        print(measure_frequency(["1", "2", "3", "bubel"]))
        
    elif(len(sys.argv) > 1 and sys.argv[1] in ["--client", "-c"]):
        import socket

        host = socket.gethostname()
        port = 8001

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((host, port))
                sock.sendall("*ID".encode())
                sock.sendall("N?\n".encode())
                data = sock.recv(1024)
                print('Received:\n' + data.decode())
                sock.sendall("meas".encode())
                sock.sendall(":wav".encode())
                sock.sendall(" 2\n".encode())
                data = sock.recv(1024)
                print('Received:\n' + data.decode())
            except ConnectionError as e:
                print(str(e))

    else:
        serv = Server()
        parser = ScpiParser()
        serv.processor = parser.process

        parser.register("*IDN?", identify)
        parser.register("MEASure:WAVelength", measure_wavelength)
        parser.register("MEASure:FREQuency", measure_frequency)

        serv.run()

