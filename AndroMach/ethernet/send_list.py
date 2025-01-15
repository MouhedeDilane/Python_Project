import socket

UDP_IP = "169.254.0.111"
UDP_PORT = 12345

# Sample list to send
data_list = ["EV0","10","20","25","30"]

# Convert list to bytes
data_bytes = bytes(data_list)

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send data
sock.sendto(data_bytes, (UDP_IP, UDP_PORT))

print(f"Sent data: {data_list}")