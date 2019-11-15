import threading
from socket import socket, error
clientes = {}
#import time

class Cliente(threading.Thread):
    def __init__(self, conn, addr):
        super(Cliente, self).__init__()
        self.conn = conn
        self.addr = addr

    def run(self):
        while self.conn:
            data = self.conn.recv(1024).decode()
            if data =="Salir" or not data:
                self.conn.send("s".encode())
                break
            print(data, self.addr)
            self.conn.send(data.encode())
        print("Sesión finalizada: ",self.addr)
        clientes[self.addr][1] = 0


if __name__ == "__main__":
    s = socket()
    s.bind(("localhost", 8000))
    s.listen(5)
    while True:
        for i in clientes:
            if clientes[i][1] == 0:
                print(clientes)
                clientes[i][0].join()
                clientes.pop(i)
                break
        print("Va a aceptar...")
        conn, addr = s.accept()
        print("Aceptó")
        c = Cliente(conn, addr)
        clientes[addr]=[c,1]
        c.start()
        print("Corrió")
