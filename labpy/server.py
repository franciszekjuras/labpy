import socket
import selectors
import types

class Server:

    def __init__(self) -> None:        
        self.read_termination = '\n'
        self.write_termination = '\n'
        self.port = 8001
        self.processor = lambda msg : msg        
        self._sel = selectors.DefaultSelector()
        self._buf = {}

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        id = addr[0] + ':' + str(addr[1])
        self._buf[id] = ""
        print("Accepted connection from", addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        # events = selectors.EVENT_READ | selectors.EVENT_WRITE
        events = selectors.EVENT_READ
        self._sel.register(conn, events, data=data)


    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        id = data.addr[0] + ':' + str(data.addr[1])
        if mask & selectors.EVENT_READ:
            try: recv_data = sock.recv(1024)  # Should be ready to read
            except ConnectionError:
                print("Connection with", id, "was aborted.")
                recv_data = None
            if recv_data:
                # print("Received:", recv_data)
                msgs = self.parse_data(recv_data, id)
                reps = self.process_data(msgs)
                for msg, rep in zip(msgs, reps):
                    print("From", id, "\n[Received]", msg, "\n[Replied ]", rep)
                for rep in reps:
                    if rep:
                        sock.sendall((rep + self.write_termination).encode())
            else:
                print("Closing connection to", id)
                del self._buf[id]
                self._sel.unregister(sock)
                sock.close()
        # if mask & selectors.EVENT_WRITE:
        #     if data.outb:
        #         print("echoing", repr(data.outb), "to", data.addr)
        #         sent = sock.send(data.outb)  # Should be ready to write
        #         data.outb = data.outb[sent:]

    def parse_data(self, data, id):
        self._buf[id] = self._buf[id] + data.decode()
        msgs = self._buf[id].split(self.read_termination)
        self._buf[id] = msgs[-1]
        return msgs[:-1]

    def process_data(self, msgs):
        return [self.processor(msg) for msg in msgs]

    def run(self):
        host = socket.gethostname()
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((host, self.port))
        lsock.listen()
        lsock.setblocking(False)
        self._sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                print("Listening on", (host, self.port))
                events = self._sel.select(timeout=1)
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
