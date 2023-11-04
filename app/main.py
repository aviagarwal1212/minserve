# Uncomment this to pass the first stage
# import socket
import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("created server on localhost:4221")
    server_socket.accept()


if __name__ == "__main__":
    main()
