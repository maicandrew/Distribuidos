import socket

s = socket.socket()
s.connect(("localhost", 8000))
while True:
    a = input("Hola: ")
    s.send(a.encode())
    a = s.recv(1024).decode()
    print(a)
    if a == "s":
        s.close()
        break
