import threading
from socket import socket, error
clientes = {}
salas = {}
#import time

class Room(threading.Thread):
    def __init__(self, name, owner = None):
        super(Room, self).__init__()
        self.owner = owner
        self.name = name
        self.users = []
        self.users.append(owner)

    def run(self):
        while len(self.users) > 0:
            for user in self.users:
                if user.message != "":
                    if user.priv == None:
                        cad = user.name+": "+user.message
                        self.send(cad.encode())
                    else:
                        cad = "/private "+user.name+": "+user.message
                        user.priv.conn.send(cad.encode())
                    user.message = ""
                if user.command != "":
                    comm = user.command
                    if comm.startswith("#cR "):
                        createRoom(comm[4:], user)
                    elif comm.startswith("#gR "):
                        getRoom(comm[4:], user)
                    elif comm == "#eR":
                        exitRoom(user)
                    elif comm == "exit":
                        exitClient(user)
                    elif comm == "#lR":
                        listRooms(user)
                    elif comm.startswith("#dR "):
                        deleteRoom(comm[4:], user)
                    elif comm == "#show users":
                        getUsuarios(user)
                    elif comm.startswith("#/private "):
                        sendPrivate(comm[10:], user)
                    else:
                        user.conn.send("Comando no reconocido".encode())
                    user.command = ""
                    #condicional para comandos
        print("Sala", self.name, "vacía. Cerrando sala")

    def send(self, message):
        for user in self.users:
            user.conn.send(message.encode())

class Cliente(threading.Thread):
    def __init__(self, conn, addr, name, room = "default"):
        super(Cliente, self).__init__()
        self.conn = conn
        self.addr = addr
        self.name = name
        self.message = ""
        self.command = ""
        self.priv = None
        self.room = room

    def run(self):
        while self.conn:
            data = self.conn.recv(1024).decode()
            if data:
                if data.startswith("#"):
                    self.command = data
                else:
                    self.message = data
            else:
                break
        print("Sesión finalizada:",self.name, self.addr)
        clientes[self.addr][1] = 0

    def join(self):
        self.conn.send("Cerrando conexión".encode())
        self.conn.close()
        self.room = None
        threading.Thread.join(self)

def createRoom(name, user = None):
    if not name in salas:
        sala = Room(name, user)
        sala.start()
        salas[name] = sala
        user.room = sala
        cad = "Sala creada: "+name
        user.conn.send(cad.encode())
    else:
        user.conn.send("Error al intentar crear la sala".encode())

def getRoom(name, user):
    if name in salas:
        sala = salas[name]
        sala.users.append(user)
        user.room = sala
        cad = "Conectado a "+name
        user.conn.send(cad.encode())
    else:
        user.conn.send("Error al intentar conectarse a la sala".encode())

def exitRoom(user):
    sala = user.room
    if sala.name != "default":
        sala.users.remove(user)
        user.room(salas["default"])
        sala["default"].users.append(user)
        user.conn.send("Saliendo a la sala por defecto".encode())

def exitClient(user):
    sala = user.room
    sala.users.remove(user)
    clientes.pop(user.name)
    user.join()

def listRooms(user):
    cad = ""
    for sala in salas:
        cad += sala+": "
        cant = len(salas[sala].users)
        if sala == "default":
            cant-=1
        cad += str(cant) + " usuarios"
        cad +="\n"
    cad = cad[:-1]
    user.conn.send(cad.encode())

def deleteRoom(name, user):
    if name in salas:
        sala = salas[name]
        if sala.owner == user.name:
            for u in sala.users:
                exitRoom(u)
            cad = "Sala " + name + " borrada"
            user.conn.send(cad.encode())
        else:
            cad = "No eres el dueño de la sala "+name
            user.conn.send(cad.encode())
    else:
        cad = "Error al intentar borrar la sala "+name
        user.conn.send(cad.encode())

def getUsuarios(user):
    cad = ""
    for user in clientes:
        cad += user+"\n"
    cad = cad[:-1]
    user.conn.send(cad.encode())

def sendPrivate(target, source):
    if target in clientes:
        source.priv = clientes[target]

if __name__ == "__main__":
    s = socket()
    s.bind(("localhost", 8000))
    s.listen(5)
    createRoom("default")
    """
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
    """