import threading
from socket import socket, error
clientes = {}
names = []
#import time

class Cliente(threading.Thread):
    def __init__(self, conn, addr, name, peer = None):
        super(Cliente, self).__init__()
        self.conn = conn
        self.addr = addr
        self.name = name
        self.peer = peer

    def run(self):
        while self.conn:
            if self.peer == None:
                print("El cliente debe seleccionar con quien chatear")
                nombres = str(names)
                conn.send(nombres.encode())
                print("Seleccionando chat")
                peer = self.conn.recv(1024).decode()
                if clientes[peer][0].peer == None:
                    self.peer = clientes[peer][0]
                    clientes[peer][0].peer = self
                    self.conn.send("yes".encode())
                    print("Cliente seleccionado")
                else:
                    self.conn.send("no".encode())
            else:
                data = self.conn.recv(1024).decode()
                self.peer.conn.send(data)
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
        print("En espera de conexión...")
        conn, addr = s.accept()
        print("Nueva conexión establecida")
        nombres = str(names)
        conn.send(nombres.encode())
        print("Seleccionando nombre...")
        name = conn.recv(1024).decode()
        print("Nombre seleccionado.")
        names.append(name)
        c = Cliente(conn, addr, name)
        clientes[name]=[c, 1]
        c.start()
        print("Corrió")
        for i in clientes:
            if clientes[i][1] == 0:
                names.pop(names.index(i))
                clientes[i][0].join()
                clientes.pop(i)
                print(clientes)
                break
