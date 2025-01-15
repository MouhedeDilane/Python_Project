from socket import *

def test_udp_client(address):
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.settimeout(2)

    try:
        client_socket.sendto(b'101001100000', address)
        print("Sent command: 101001100000")

        response, addr = client_socket.recvfrom(1024)
        print(f"Received response: {response.decode()} from {addr}")

    except timeout:
        print("No response received - request timed out")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        client_socket.close()

if __name__ == "__main__":
    test_udp_client(('192.168.0.149', 12345))