import socket

# IP address and port of the STM32 microcontroller
UDP_IP = "169.254.0.111"
UDP_PORT = 12345  # Replace with the actual port number

# File containing data to send
DATA_FILE = "ethernet.txt"

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def read_values_after_event(event):
    values = []
    with open(DATA_FILE, 'r') as file:
        for line in file:
            if line.startswith(event):
                # Split the line by ',' and retrieve the values after the event
                event_data = line.strip().split(',')[1:]  # Remove the event identifier and split by ','
                values = [int(val) for val in event_data]  # Convert each value to int
                break  # Break after finding values
    return values

# Send function
def send_data(data_string):
    sock.sendto(data_string.encode(), (UDP_IP, UDP_PORT))
    print(f"Sent data to {UDP_IP}:{UDP_PORT}: {data_string}")

# Send initial data to STM32 (first line)
with open(DATA_FILE, 'r') as file:
    first_line = file.readline().strip()
    sock.sendto(first_line.encode(), (UDP_IP, UDP_PORT))
    print(f"Sent initial data to {UDP_IP}:{UDP_PORT}: {first_line}")

# Listen for the confirmation message (ACK)
sock.settimeout(5)  # Set a timeout for receiving the confirmation
try:
    data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
    ack_message = data.decode()
    print(f"Received ACK from {addr}: {ack_message}")

    # Wait for user input (you can customize this part)
    input("Press Enter to continue...")

    list1 = read_values_after_event("EV0")
    list2 = read_values_after_event("EV1")
    list3 = read_values_after_event("EV2")
    print(list1)
    print(list2)
    print(list3)
    sequence = []
    for element in [list1, list2, list3]:
        sequence.append("0xFF")  # Append "0xFF" as a string
        sequence.extend(map(str, element))  # Convert each int to str and extend the list
        
    data_string = ",".join(sequence)  # Join the sequence list into a single string separated by commas
    print(data_string)
    send_data(data_string)
except socket.timeout:
    print("No confirmation received within the timeout period")
finally:
    sock.close()