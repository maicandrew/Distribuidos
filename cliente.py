import socket
import threading

class listener(threading.Thread):
    def __init__(self, sock):
        super(listener, self).__init__()
        self.sock = sock

    def run(self):
        while self.sock:
            message = self.sock.recv(1024)
            print(peer+":", message)

s = socket.socket()
s.connect(("localhost", 8000))
name = ""
peer = ""
while True:
    names = s.recv(1024).decode()[1:-1].split(", ")
    while name == "":
        name = input("Ingrese un nombre para regitrarse: ")
    if not repr(name) in names:
        print("Nombre válido.")
        s.send(name.encode())
        break
    else:
        print("Nombre en uso, elija otro.")

while True:
    names = s.recv(1024).decode()[1:-1].split(", ")
    for n in names:
        if n[1:-1] != name:
            print (n[1:-1])
    peer = input("Seleccione con quien chatear: ")
    while peer == "":
        peer = input("Seleccione con quien chatear: ")
    if repr(peer) in names:
        s.send(peer.encode())
        r = s.recv(10).decode()
        if r == "yes":
            print("Chat seleccionado")
            break
        else:
            print("El usuario ya se encuentra conectado con alguien más. Intente con otro nombre")
    else:
        print("Nombre inválido")

while True:
    l = listener(s)
    l.start()
    a = input(name)
    while a == "":
        a = input(name)
    s.send(a.encode())
    print(a)
    if a == "s":
        s.close()
        break
