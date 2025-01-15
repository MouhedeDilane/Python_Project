import socket

def send_udp_message(message, target_ip, target_port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Send the message
        sock.sendto(message.encode('utf-8'), (target_ip, target_port))
        print(f"Sent message: {message} to {target_ip}:{target_port}")
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        # Close the socket
        sock.close()

# Define the target IP address and port
TARGET_IP = '169.254.108.100'  # Change this to the target IP address
TARGET_PORT = 12345           # Change this to the target port

# Message to be sent
message = "E,1000,2000,2500,3000,E,1000,3000,E,2000,3000,3500,E,1000,2000,2500,3000,E,1000,3000,E,1000,2000,3000,4000,5000,E,1000,2000,2500,3000"
# Send the message
send_udp_message(message, TARGET_IP, TARGET_PORT)