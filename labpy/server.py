import socket
import selectors
import types

class Server:

    def __init__(self) -> None:        
        self.read_termination = '\n'
        self.write_termination = '\n'
        self.port = 8001
        class _EchoProcessor:
            def process(self, msg):
                return msg
        self.processor = _EchoProcessor()
        
        self._sel = selectors.DefaultSelector()
        self._buf = ""

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("Accepted connection from", addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        # events = selectors.EVENT_READ | selectors.EVENT_WRITE
        events = selectors.EVENT_READ
        self._sel.register(conn, events, data=data)


    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            try: recv_data = sock.recv(1024)  # Should be ready to read
            except ConnectionError:
                print("Connection with", data.addr[0], "was aborted.")
                recv_data = None
            if recv_data:
                msgs = self.parse_data(recv_data)
                for msg in msgs:
                    print("Received command from", data.addr[0])
                    print(msg)
                repl = self.process_data(msgs)
                for rep in repl:
                    if rep:
                        sock.sendall((rep + self.write_termination).encode())
            else:
                print("Closing connection to", data.addr)
                self._sel.unregister(sock)
                sock.close()
        # if mask & selectors.EVENT_WRITE:
        #     if data.outb:
        #         print("echoing", repr(data.outb), "to", data.addr)
        #         sent = sock.send(data.outb)  # Should be ready to write
        #         data.outb = data.outb[sent:]

    def parse_data(self, data):
        global buf 
        self._buf += data.decode()
        msgs = self._buf.split(self.read_termination)
        buf = msgs[-1]
        return msgs[:-1]

    def process_data(self, msgs):
        return [self.processor.process(msg) for msg in msgs]
        # repl = []
        # for msg in msgs:
        #     print("Executing: " + msg)
        #     repl.append("Sie robi")
        # return repl


    # if len(sys.argv) != 3:
    #     print("usage:", sys.argv[0], "<host> <port>")
    #     sys.exit(1)

    # host, port = sys.argv[1], int(sys.argv[2])
    def run(self):
        host = socket.gethostname()
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((host, self.port))
        lsock.listen()
        print("listening on", (host, self.port))
        lsock.setblocking(False)
        self._sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = self._sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting...")
        finally:
            self._sel.close()

if (__name__ == "__main__"):
    serv = Server()
    serv.run()