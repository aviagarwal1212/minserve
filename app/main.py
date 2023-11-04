import asyncio
from dataclasses import dataclass
from http import HTTPStatus

RESPONSE_SEP = "\r\n"
PORT = 4221
BUFFER_SIZE = 2048


@dataclass
class HTTPResponse:
    content: str | None = None
    content_type: str | None = None
    content_length: int | None = None
    status: HTTPStatus = HTTPStatus.NOT_FOUND

    def __post_init__(self):
        if self.content is not None:
            self.content_length = len(self.content)
            self.content_type = "text/plain"

    async def return_byte_response(self) -> bytes:
        response_string = f"HTTP/1.1 {self.status}{RESPONSE_SEP}"
        if self.content is not None:
            response_string += f"Content-Type: {self.content_type}{RESPONSE_SEP}"
            response_string += f"Content-Length: {self.content_length}{RESPONSE_SEP*2}"
            response_string += f"{self.content}{RESPONSE_SEP}"
        response_string += f"{RESPONSE_SEP}"
        return response_string.encode()


@dataclass
class HTTPRequest:
    method: str
    path: str
    http_version: str
    headers: list[str]

    async def request_headers(self) -> dict[str, str]:
        header_dict: dict[str, str] = {}
        for header in self.headers:
            if header != "":
                header_type, header_content = header.split(": ")
                header_dict[header_type.strip()] = header_content.strip()

        return header_dict

    async def process_response(self) -> HTTPResponse:
        status = HTTPStatus.NOT_FOUND
        content: str | None = None
        match self.path:
            case "/":
                status = HTTPStatus.OK

            case path if path.startswith("/echo/"):
                status = HTTPStatus.OK
                content = path.split("/echo/")[1]

            case "/user-agent":
                status = HTTPStatus.OK
                headers = await self.request_headers()
                content = headers["User-Agent"]

            case _:
                ...

        return HTTPResponse(content=content, status=status)


async def process_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    request = await process_connection(reader)
    print(f"received {request.method} request on {request.path}")
    response = await request.process_response()
    response_bytes = await response.return_byte_response()
    writer.write(response_bytes)
    writer.close()


async def process_connection(reader: asyncio.StreamReader) -> HTTPRequest:
    request_bytes = await reader.read(BUFFER_SIZE)
    request = request_bytes.decode()
    start_line, *headers = request.split(RESPONSE_SEP)
    method, path, http_version = start_line.split(" ")
    return HTTPRequest(method, path, http_version, headers)


async def main():
    server = await asyncio.start_server(process_client, host="localhost", port=PORT)
    print(f"created server on localhost:{PORT}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
