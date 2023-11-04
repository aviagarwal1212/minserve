# Uncomment this to pass the first stage
# import socket
import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("created server on localhost:4221")
    connection, ret_add = server_socket.accept()
    print(f"connected to {connection} at {ret_add}")
    with connection:
        connection.recv(512)
        connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        print("-> responded to connection")


if __name__ == "__main__":
    main()
