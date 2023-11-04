# Uncomment this to pass the first stage
# import socket
from socket import socket, create_server
from dataclasses import dataclass
from http import HTTPStatus
from typing import Tuple

RESPONSE_SEP: str = "\r\n"


@dataclass
class Request:
    method: str
    path: str
    http_version: str
    headers: list[str]


@dataclass
class Response:
    content: str | None = None
    content_type: str | None = None
    content_length: int | None = None
    status: HTTPStatus = HTTPStatus.NOT_FOUND

    def __post_init__(self):
        if self.content is not None:
            self.content_length = len(self.content)

    def return_byte_response(self) -> bytes:
        response_string = f"HTTP/1.1 {self.status}{RESPONSE_SEP}"
        if self.content is not None:
            response_string += f"Content-Type: {self.content_type}{RESPONSE_SEP}"
            response_string += f"Content-Length: {self.content_length}{RESPONSE_SEP*2}"
            response_string += f"{self.content}{RESPONSE_SEP*2}"
        else:
            response_string += f"{RESPONSE_SEP}"
        return response_string.encode()


def main():
    server_socket = create_server(("localhost", 4221), reuse_port=True)
    print("created server on localhost:4221")
    connection, ret_add = server_socket.accept()
    with connection:
        request = process_connection(connection)
        print(f"received {request.method} request on {request.path}")
        response = process_response(request)
        response_bytes = response.return_byte_response()
        connection.sendall(response_bytes)


def process_connection(connection: socket) -> Request:
    request = connection.recv(2048).decode()
    start_line, *headers = request.split("\r\n")
    method, path, http_version = start_line.split(" ")
    return Request(method, path, http_version, headers)


def process_response(request: Request) -> Response:
    status = HTTPStatus.NOT_FOUND
    content: str | None = None
    content_type: str | None = None
    match request.path:
        case "/":
            status = HTTPStatus.OK
        case path if path.startswith("/echo/"):
            status = HTTPStatus.OK
            content = path.split("/echo/")[1]
            content_type = "text/plain"
        case _:
            ...

    return Response(content=content, content_type=content_type, status=status)


if __name__ == "__main__":
    main()
