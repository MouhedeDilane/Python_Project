import serial

# Define the COM port and the baud rate
port = 'COM5'
baud_rate = 9600  # Set this to the baud rate of your device

# Initialize the serial connection
ser = serial.Serial(port, baud_rate, timeout=1)

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
except KeyboardInterrupt:
    print("Exiting program.")
finally:
    ser.close()