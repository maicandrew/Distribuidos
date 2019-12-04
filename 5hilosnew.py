import threading
import pymongo
from socket import socket, error
uri  = "***REMOVED***"
client = pymongo.MongoClient(uri)
db = client.App
DBUsers = db.Users
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
                if user != None:
                    if user.message != "":
                        if user.priv == None:
                            cad = user.name+": "+user.message
                            self.send(cad)
                        else:
                            cad = "/private "+user.name+": "+user.message
                            user.priv.conn.send(cad.encode())
                            user.priv = None
                        user.message = ""
                    if user.command != "":
                        comm = user.command
                        if comm.startswith("#cR "):
                            createRoom(comm[4:], user)
                        elif comm.startswith("#gR "):
                            getRoom(comm[4:], user)
                        elif comm == "#eR":
                            exitRoom(user)
                        elif comm == "#exit":
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
            if user != None:
                user.conn.send(message.encode())

class Cliente(threading.Thread):
    def __init__(self, conn, addr, name = ""):
        super(Cliente, self).__init__()
        self.conn = conn
        self.addr = addr
        self.name = name
        self.message = ""
        self.command = ""
        self.priv = None
        self.room = None

    def run(self):
        while True:
            if self.name == "":
                data = self.conn.recv(1024).decode()
                if data == "#mode:register":
                    valid = True
                    while valid:
                        nombrer = self.conn.recv(1024).decode()
                        #Comprobar en la base de datos si el usuario ya existe
                        cant = DBUsers.find_one({"username": nombrer})
                        if cant == None:
                            valid = False
                        self.conn.send(str(valid).encode())
                    nombres = self.conn.recv(1024).decode()
                    apellidos = self.conn.recv(1024).decode()
                    usuario = self.conn.recv(1024).decode()
                    password = self.conn.recv(1024).decode()
                    edad = self.conn.recv(1024).decode()
                    genero = self.conn.recv(1024).decode()
                    #Insertar en la base de datos
                    try:
                        if usuario != "":
                            a = DBUsers.insert_one({"username": usuario, "nombres": nombres,
                                            "apellidos": apellidos, "password":password,
                                            "edad": edad, "genero": genero})
                            print("Usuario nuevo registrado:",a.inserted_id)
                    except:
                        print("Error al insertar en la base de datos")
                elif data == "#mode:login":
                    document = None
                    invalid = True
                    while invalid:
                        try:
                            nombrel = self.conn.recv(1024).decode()
                        except:
                            break
                        #Comprobar en la base de datos si el usuario ya existe
                        document = DBUsers.find_one({"username": nombrel})
                        if document != None:
                            invalid = False
                        self.conn.send(str(invalid).encode())
                    passw = True
                    while passw:
                        try:
                            contrasena = self.conn.recv(1024).decode()
                        except:
                            break
                        #Comprobar en la base de datos si el usuario ya existe
                        if contrasena == document["password"]:
                            passw = False
                        self.conn.send(str(passw).encode())
                    username = self.conn.recv(1024).decode()
                    self.name = username
                    self.log()
            else:
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

    def log(self):
        clientes[self.name] = self
        self.room = salas["default"]
        self.room.users.append(self)

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
        cad = "Sala creada: "+name
        if user != None:
            user.room.users.remove(user)
            user.room = sala
            user.conn.send(cad.encode())
    else:
        if user != None:
            user.conn.send("Error al intentar crear la sala".encode())

def getRoom(name, user):
    if name in salas:
        sala = salas[name]
        sala.users.append(user)
        user.room.users.remove(user)
        user.room = sala
        cad = "Conectado a "+name
        user.conn.send(cad.encode())
    else:
        user.conn.send("Error al intentar conectarse a la sala".encode())

def exitRoom(user):
    sala = user.room
    if sala.name != "default":
        sala.users.remove(user)
        user.room = salas["default"]
        salas["default"].users.append(user)
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
        if name != "default":
            if sala.owner.name == user.name:
                for u in sala.users:
                    exitRoom(u)
                cad = "Sala " + name + " borrada"
                user.conn.send(cad.encode())
            else:
                cad = "No eres el dueño de la sala "+name
                user.conn.send(cad.encode())
        else:
            cad = "No puedes borrar la sala por defecto"
            user.conn.send(cad.encode())
    else:
        cad = "Error al intentar borrar la sala "+name
        user.conn.send(cad.encode())

def getUsuarios(user):
    cad = ""
    for u in clientes:
        cad += u+"\n"
    cad = cad[:-1]
    user.conn.send(cad.encode())

def sendPrivate(target, source):
    if target in clientes:
        source.priv = clientes[target]
    else:
        source.conn.send("El usuario al que intenta enviar el mensaje no se encuentra en linea".encode())

if __name__ == "__main__":
    s = socket()
    s.bind(("localhost", 8000))
    s.listen(5)
    createRoom("default")
    while True:
        print("En espera de conexión...")
        conn, addr = s.accept()
        print("Cliente conectado")
        client = Cliente(conn,addr)
        client.start()
