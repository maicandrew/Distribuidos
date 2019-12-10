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
                        if comm.startswith("#cR"):
                            createRoom(espacios(comm[4:]), user)
                        elif comm.startswith("#gR"):
                            getRoom(espacios(comm[4:]), user)
                        elif comm == "#eR":
                            exitRoom(user)
                        elif comm == "#exit":
                            exitClient(user)
                        elif comm == "#lR":
                            listRooms(user)
                        elif comm.startswith("#dR"):
                            deleteRoom(espacios(comm[4:]), user)
                        elif comm == "#show users":
                            getUsuarios(user)
                        elif comm.startswith("#/private "):
                            sendPrivate(espacios(comm[10:]), user)
                        elif comm == "#help":
                            showHelp(user)
                        else:
                            user.conn.send("Comando no reconocido, utilice el comando #help para ver el uso correcto de los comandos".encode())
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
                try:
                    data = self.conn.recv(1024).decode()
                except ConnectionAbortedError:
                    print("Al parecer el cliente se ha desconectado")
                    return False
                if data == "#mode:register":
                    valid = True
                    while valid:
                        try:
                            nombrer = self.conn.recv(1024).decode()
                        except ConnectionAbortedError:
                            print("Al parecer el cliente se ha desconectado")
                            return False
                        #Comprobar en la base de datos si el usuario ya existe
                        cant = DBUsers.find_one({"username": nombrer})
                        if cant == None:
                            valid = False
                        self.conn.send(str(valid).encode())
                    try:
                        nombres = self.conn.recv(1024).decode()
                        apellidos = self.conn.recv(1024).decode()
                        usuario = self.conn.recv(1024).decode()
                        password = self.conn.recv(1024).decode()
                        edad = self.conn.recv(1024).decode()
                        genero = self.conn.recv(1024).decode()
                    except ConnectionAbortedError:
                        print("Al parecer el cliente se ha desconectado")
                        return False
                    #Insertar en la base de datos
                    try:
                        if usuario != "":
                            a = DBUsers.insert_one({"username": usuario, "nombres": nombres,
                                            "apellidos": apellidos, "password":password,
                                            "edad": edad, "genero": genero})
                            print("Usuario nuevo registrado:",a.inserted_id)
                    except Exception as e:
                        print("Error al insertar en la base de datos:", e)
                elif data == "#mode:login":
                    document = None
                    invalid = True
                    try:
                        nombrel = self.conn.recv(1024).decode()
                    except ConnectionAbortedError:
                        print("Al parecer el cliente se ha desconectado")
                        return False
                    #Comprobar en la base de datos si el usuario ya existe
                    document = DBUsers.find_one({"username": nombrel})
                    if document != None:
                        invalid = False
                    self.conn.send(str(invalid).encode())
                    if not invalid:
                        passw = True
                        while passw:
                            try:
                                contrasena = self.conn.recv(1024).decode()
                            except ConnectionAbortedError:
                                print("Al parecer el cliente se ha desconectado")
                                return False
                            #Comprobar en la base de datos si el usuario ya existe
                            if contrasena == document["password"]:
                                passw = False
                            self.conn.send(str(passw).encode())
                        username = self.conn.recv(1024).decode()
                        self.name = username
                        self.log()
            else:
                while self.conn:
                    try:
                        data = self.conn.recv(1024)
                    except (ConnectionResetError, ConnectionAbortedError):
                        print("Sesión finalizada:",self.name, self.addr)
                        return False
                    if data:
                        data  = data.decode()
                        if data.startswith("#"):
                            self.command = data
                        else:
                            self.message = data
                    else:
                        break
                    

    def log(self):
        clientes[self.name] = self
        self.room = salas["default"]
        self.room.users.append(self)

    def join(self):
        self.conn.close()
        self.name = ""
        self.room = None
        threading.Thread.join(self)

def espacios(st):
    while st.startswith(" "):
        st = st[1:]
    while st.endswith(" "):
        st = st[:-1]
    return st

def createRoom(name, user = None):
    if name != "":
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
    else:
        user.conn.send("Uso incorrecto del comando. Utilice #help para obtener ayuda")


def getRoom(name, user):
    if name != "":
        if name in salas:
            sala = salas[name]
            sala.users.append(user)
            user.room.users.remove(user)
            user.room = sala
            cad = "Conectado a "+name
            user.conn.send(cad.encode())
        else:
            user.conn.send("Error al intentar conectarse a la sala".encode())
    else:
        user.conn.send("Uso incorrecto del comando. Utilice #help para obtener ayuda")

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
    if name != "":
        if name in salas:
            sala = salas[name]
            if name != "default":
                if sala.owner.name == user.name:
                    for u in sala.users:
                        exitRoom(u)
                    salas.pop([name])
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
    else:
        user.conn.send("Uso incorrecto del comando. Utilice #help para obtener ayuda")

def showHelp(user):
    cad = "Los comandos disponibles con su respectivo uso correcto son:\n"
    cad += "'#cR <nombreSala>': Crear sala con el nombre nombreSala. El servidor de forma automática ingresa a este cliente a la sala que creó\n"
    cad += "'#gR <nombreSala>': Entrar a la sala nombreSala\n"
    cad += "'#eR': Salir de la sala en que se encuentra. El servidor enviara al cliente a la sala por defecto. Si el cliente ingresa este comando estando en la sala por defecto, no tendrá ningún efecto\n"
    cad += "'#exit': Desconectará al cliente del servidor\n"
    cad += "'#lR': Lista los nombres de todas las sala disponibles y el número de participantes de cada una\n"
    cad += "'#dR <nombreSala>': Elimina la sala nombreSala. Un cliente solo puede eliminar las salas que creo\n"
    cad += "'#show users': Muestra el listado el todos los usuarios en todo el sistema\n"
    cad += "'#\\private <nombreusuario>': El siguiente mensaje que se escriba se enviará de forma privada al usuario nombreusuario sin importar la sala en la que esté"
    user.conn.send(cad.encode())

def getUsuarios(user):
    cad = "Clientes en linea:\n"
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
    try:
        while True:
            print("En espera de conexión...")
            conn, addr = s.accept()
            print("Cliente conectado:", addr)
            client = Cliente(conn,addr)
            client.start()
    except KeyboardInterrupt:
        for sala in salas:
            salas[sala].join()
            salas.pop(sala)
        for cliente in clientes:
            clientes[cliente].join()
