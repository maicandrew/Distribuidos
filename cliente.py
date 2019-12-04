import socket
import threading
import hashlib
from time import sleep

class listener(threading.Thread):
    def __init__(self, sock):
        super(listener, self).__init__()
        self.sock = sock

    def run(self):
        while self.sock:
            message = self.sock.recv(1024).decode()
            print(message)

def encrypt_string(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

def espacios(st):
    while st.startswith(" "):
        st = st[1:]
    while st.endswith(" "):
        st = st[:-1]
    return st

def login(s):
    password = ""
    usuario = espacios(input("Usuario: "))
    while usuario == "":
            usuario = espacios(input("Usuario: "))
    if newUser(s, usuario) == "False":
        while True:
            password = espacios(input("Contraseña: "))
            while password == "":
                password = espacios(input("Contraseña: "))
            password = encrypt_string(password)
            if newUser(s, password) == "False":
                s.send(usuario.encode())
                return True
            else:
                print("La contraseña que está usando no es correcta.")
    else:
        print("El usuario con el que intenta ingresar no está registrado.")
        return False

def newUser(s, username):
    s.send(username.encode())
    r = s.recv(1024).decode()
    return r

def register(s):
    usuario = ""
    while True:
        usuario = espacios(input("Usuario: "))
        while usuario == "":
                usuario = espacios(input("Usuario: "))
        if newUser(s, usuario) == "True":
            print("Al parecer alguien ha usado ese nombre antes, intenta con otro.")
        else:
            break
    nombres = espacios(input("Nombres: "))
    while nombres == "":
        nombres = espacios(input("Nombres: "))
    apellidos = espacios(input("Apellidos: "))
    while apellidos == "":
        apellidos = espacios(input("Apellidos: "))
    password = espacios(input("Contraseña: "))
    while password == "":
        password = espacios(input("Contraseña: "))
    edad = espacios(input("Edad: "))
    while True:
        try:
            int(edad)
            break
        except:
            edad = espacios(input("Edad: "))
    genero = espacios(input("Genero(F/M): "))
    while genero != "F" and genero != "M":
        genero = espacios(input("Genero(F/M): "))
    password = encrypt_string(password)
    s.send(nombres.encode())
    sleep(0.2)
    s.send(apellidos.encode())
    sleep(0.2)
    s.send(usuario.encode())
    sleep(0.2)
    s.send(password.encode())
    sleep(0.2)
    s.send(edad.encode())
    sleep(0.2)
    s.send(genero.encode())

def name_select(s, name):
    while True:
        names = s.recv(1024).decode()[1:-1].split(", ")
        while name == "":
            name = input("Ingrese un nombre para regitrarse: ")
        if not repr(name) in names:
            print("Nombre válido.")
            s.send(name.encode())
            return name
        else:
            print("Nombre en uso, elija otro.")

def peer_select(s):
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

def menu(s):
    while True:
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("3. Salir")
        op = espacios(input("Seleccione una opción: "))
        if op == "1":
            s.send("#mode:login".encode())
            if login(s):
                 return True
        elif op == "2":
            s.send("#mode:register".encode())
            register(s)
            print("Registro completado con exito. Volviendo al menu principal...")
        else:
            return None

if __name__ == "__main__":
    s = socket.socket()
    s.connect(("localhost", 8000))
    name = ""
    peer = ""
    x = menu(s)
    if x != None:
        while True:
            l = listener(s)
            l.start()
            a = input(">")
            while a == "":
                a = input(">")
            s.send(a.encode())
            if a == "s":
                s.close()
                break
