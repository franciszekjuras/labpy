import sys
import os
import random
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from labpy.server import Server
from labpy.scpi_parser import ScpiParser

def identify(args):
    return "LabPy,Python SCPI server,NA,v21.11a"

def get_wavelength(ch):
    return str(float(ch) + random.uniform(-1,1))

def measure_wavelegnth(args):
    res = []
    for i_s in args:
        try:
            i = int(i_s)
            if(i >= 0 and i <= 8):
                res.append(get_wavelength(i))
        except ValueError:
            pass
    return ','.join(res)

if(__name__ == "__main__"):

    if(len(sys.argv) > 1 and sys.argv[1] in ["--client", "-c"]):
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
        random.seed(42)

        parser.register("*IDN?", identify)
        parser.register("MEASure:WAVelength", measure_wavelegnth)

        serv.run()

