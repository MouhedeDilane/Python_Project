from socket import *
import csv

address= ( '192.168.0.101', 5000) #define server IP and port
client_socket =socket(AF_INET, SOCK_DGRAM) #Set up the Socket
client_socket.settimeout(1) #Only wait 1 second for a response

column_name = ["P1", "P2", "P3"]

with open('data.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(column_name)
    file.close()

input("Enter to continue")
client_socket.sendto(b"TEST", address)

dataframe = [column_name]

while True:
    try:
        data, addr = client_socket.recvfrom(2048) #Read response from arduino
        if data!=b'Exit':

            a = []
            for i in range(4, len(data), 2):
                a1 = (int(data[i]) << 8
                | int(data[i+1]))
                a.append(a1)

            with open('data.csv', 'a') as file:
                writer = csv.writer(file)
                writer.writerow(a)
            
            dataframe.append(a)

        if data==b'Exit':
            print(data)
            print("Done")
            break
 
    except:
        print("No data received")
        pass
