import socket
import threading
import csv

# Global variables for shared data
received_data = []
csv_file = 'received_data.csv'

def send_binary_number_and_sequence(binary_number, sequences):
    server_address = ('169.254.182.198', 12345)  # STM32 IP and port
    message = binary_number.encode('utf-8')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)  # Set a timeout for receiving the response

    try:
        # Send the binary number to the STM32
        sock.sendto(message, server_address)
        
        # Wait for the confirmation message
        response, _ = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        print("Received confirmation:", response.decode('utf-8'))
        
        # Format sequences into the required string format
        formatted_sequences = ','.join([f"E,{','.join(map(str, seq))}" for seq in sequences])
        formatted_sequences = formatted_sequences.encode('utf-8')
        
        # Send the formatted sequences to the STM32
        sock.sendto(formatted_sequences, server_address)
        print("Sent sequences to STM32:", formatted_sequences.decode('utf-8'))

    except socket.timeout:
        print("No response received from the server.")
    finally:
        sock.close()

def udp_listener():
    global received_data
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', 12345)  # Listen on all interfaces, port 12345
    sock.bind(server_address)

    try:
        while True:
            data, _ = sock.recvfrom(1024)  # Adjust buffer size as needed
            received_data.append(data.decode('utf-8'))
            print("Received data from STM32:", data.decode('utf-8'))
            
            # Write received data to CSV file
            with open(csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([data.decode('utf-8')])
                
    finally:
        sock.close()

if __name__ == "__main__":
    try:
        # Start the UDP listener thread
        udp_thread = threading.Thread(target=udp_listener)
        udp_thread.start()

        # Continue with original script logic
        with open('ethernet.txt', 'r') as file:
            binary_number = file.readline().strip()
            sequences = [list(map(int, line.strip().split(',')[1:])) for line in file.readlines()]
            
        if len(binary_number) == 3 and all(bit in '01' for bit in binary_number):
            send_binary_number_and_sequence(binary_number, sequences)
        else:
            print("Invalid binary number. Please enter exactly 3 digits consisting of 0s and 1s.")

        # Wait for UDP listener thread to finish
        udp_thread.join()

    except FileNotFoundError:
        print("The file ethernet.txt was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
