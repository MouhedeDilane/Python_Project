# import socket
# import time

# # Configuration
# UDP_IP = "169.254.108.100"  # Replace with the target IP address
# UDP_PORT = 12345           # Replace with the target port number
# MESSAGE_ON = "ON"
# MESSAGE_OFF = "OFF"

# # Create a UDP socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# try:
#     while True:
#         n=input()
#         sock.sendto(n.encode(), (UDP_IP, UDP_PORT))
#         print(f"Sent: {n}")

# except KeyboardInterrupt:
#     print("Interrupted by user")

# finally:
#     sock.close()
#     print("Socket closed")

def modify_binary(binary_number, position, value):
    # Convert binary_number to a list to modify individual bits
    binary_list = list(binary_number)

    # Convert position to zero-indexed
    index = position - 1

    # Modify the specified bit position
    binary_list[index] = str(value)

    # Join the list back into a string
    modified_binary = ''.join(binary_list)
    
    return modified_binary

while(1):
    binary_number = "1010101"  # Example 7-digit binary number
    position = int(input("pos"))  # Example position to modify (1-based index)
    value = int(input("val"))  # Example value to set at the specified position (0 or 1)

    binary_list = list(binary_number)

        # Convert position to zero-indexed
    index = 7-position

        # Modify the specified bit position
    binary_list[index] = str(value)

        # Join the list back into a string
    modified_binary = ''.join(binary_list)
    print(modified_binary,type(modified_binary))