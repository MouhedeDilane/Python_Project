import socket

UDP_IP = "169.254.49.149"  # The IP address to listen on
UDP_PORT = 12345           # The port to listen on

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on {UDP_IP}:{UDP_PORT}")

while True:
    data, addr = sock.recvfrom(256)  # buffer size is 256 bytes
    print(data.decode('utf-8'))