import socket
import datetime
import threading
import hashlib
from time import sleep, time

class listener(threading.Thread):
    def __init__(self, sock):
        super(listener, self).__init__()
        self.sock = sock
        self.stop = False

    def run(self):
        while not self.stop:
            try:
                message = self.sock.recv(1024)
            except ConnectionAbortedError:
                print("Desconectado")
                self.stop = True
            if not self.stop:
                message = message.decode()
                if message == "#time":
                    self.sock.send(str("#time " + str(datetime.datetime.now())).encode())
                else:
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
        print("El usuario con el que intenta ingresar no está registrado o ya se encuentre conectado desde otro ordenador.")
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

def menu(s):
    while True:
        try:
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
        except KeyboardInterrupt:
            return None

if __name__ == "__main__":
    s = socket.socket()
    s.connect(("localhost", 8000))
    x = menu(s)
    if x != None:
        l = listener(s)
        l.start()
        while True:
            try:
                a = input(">")
                while a == "":
                    a = input(">")
                if a != "#exit":
                    s.send(a.encode())
                else:
                    raise KeyboardInterrupt
            except KeyboardInterrupt:
                l.sock.close()
                l.stop = True
                l.join()
                break
