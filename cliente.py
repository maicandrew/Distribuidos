import socket
import threading

class listener(threading.Thread):
    def __init__(self, sock, peer = None):
        super(listener, self).__init__()
        self.sock = sock
        self.peer = peer
        self.not = False

    def run(self):
        while self.sock:
            message = self.sock.recv(1024)
            if self.peer != None:
                print(self.peer+":", message)
            else:
                print("Alguien quiere conectarse contigo: ", message)

def name_choice(s):
    while True:
        names = s.recv(1024).decode()[1:-1].split(", ")
        if names != "":
            while name == "":
                name = input("Ingrese un nombre para regitrarse: ")
            if not repr(name) in names:
                print("Nombre válido.")
                s.send(name.encode())
                break
            else:
                print("Nombre en uso, elija otro.")

def peer_choice(s):
    while True:
        names = s.recv(1024).decode()[1:-1].split(", ")
        for n in names:
            if n[1:-1] != name:
                print (n[1:-1])
        peer = input("Seleccione con quien chatear: ")
        while peer == "" and :
            peer = input("Seleccione con quien chatear: ")
        if repr(peer) in names:
            s.send(peer.encode())
            r = s.recv(100).decode()
            if r == "yes":
                print("Chat seleccionado")
                break
            else:
                print("El usuario ya se encuentra conectado con alguien más. Intente con otro nombre")
        else:
            print("Nombre inválido")

if __name__=="__main__":
    s = socket.socket()
    port = int(input("Puerto: "))
    s.connect(("localhost", port))
    name = ""
    peer = ""
    while True:
        name_choice(s)
        peer_choice(s)
        l = listener(s)
        l.start()
        a = input(name+": ")
        while a == "":
            a = input(name+": ")
        s.send(a.encode())
        if a == "s":
            l.peer = None
            peer_choice(s)
            break
