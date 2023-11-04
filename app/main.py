# Uncomment this to pass the first stage
# import socket
import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("created server on localhost:4221")
    connection, ret_add = server_socket.accept()
    with connection:
        request = connection.recv(512).decode()
        start_line, *headers = request.split("\r\n")
        method, path, http_version = start_line.split(" ")
        print(f"received {method} request on {path}")
        match path:
            case "/":
                connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
            case _:
                connection.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


if __name__ == "__main__":
    main()
