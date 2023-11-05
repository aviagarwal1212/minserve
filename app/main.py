import asyncio
import time
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from http import HTTPStatus
from pathlib import Path

PORT = 4221
BUFFER_SIZE = 2048
RESPONSE_SEP = "\r\n"


def logger(string: str):
    log_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"{log_time} | {string}")


Directory = Path | None


class HTTPContentType(Enum):
    TEXT = "text/plain"
    OCTET = "application/octet-stream"


@dataclass
class HTTPResponse:
    content: str | None = None
    content_type: HTTPContentType = HTTPContentType.TEXT
    status: HTTPStatus = HTTPStatus.OK

    @property
    def content_length(self) -> int | None:
        if self.content is not None:
            return len(self.content)
        return None

    @property
    def byte_response(self) -> bytes:
        response_string = f"HTTP/1.1 {self.status}{RESPONSE_SEP}"
        if self.content is not None:
            response_string += f"Content-Type: {self.content_type.value}{RESPONSE_SEP}"
            response_string += f"Content-Length: {self.content_length}{RESPONSE_SEP*2}"
            response_string += f"{self.content}{RESPONSE_SEP}"
        response_string += f"{RESPONSE_SEP}"
        return response_string.encode()


HTTPHeaders = dict[str, str]


@dataclass
class HTTPRequest:
    method: str
    path: str
    http_version: str
    headers: list[str]
    body: str | None = None

    @property
    def headers_dict(self) -> HTTPHeaders:
        header_dict: HTTPHeaders = {}
        for header in self.headers:
            if header != "":
                header_type, header_content = header.split(": ")
                header_dict[header_type.strip()] = header_content.strip()

        return header_dict


async def process_response(request: HTTPRequest) -> HTTPResponse:
    match request.path:
        case "/":
            return HTTPResponse()

        case path if path.startswith("/echo/"):
            content = path.split("/echo/")[1]
            return HTTPResponse(content=content)

        case "/user-agent":
            headers = request.headers_dict
            content = headers["User-Agent"]
            return HTTPResponse(content=content)

        case path if path.startswith("/files/"):
            match request.method:
                case "GET":
                    filename = path.split("/files/")[1].strip()
                    if directory is not None:
                        file = directory.joinpath(filename)
                        if file.is_file():
                            content = file.read_text()
                            return HTTPResponse(
                                content=content, content_type=HTTPContentType.OCTET
                            )

                    return HTTPResponse(status=HTTPStatus.NOT_FOUND)

                case "POST":
                    filename = path.split("/files/")[1].strip()
                    if (
                        filename != ""
                        and directory is not None
                        and request.body is not None
                    ):
                        file = directory.joinpath(filename)
                        with file.open("w", encoding="UTF-8") as f:
                            f.write(request.body)
                        return HTTPResponse(status=HTTPStatus.CREATED)

                    return HTTPResponse(status=HTTPStatus.NOT_FOUND)

                case _:
                    return HTTPResponse(status=HTTPStatus.NOT_FOUND)

        case _:
            return HTTPResponse(status=HTTPStatus.NOT_FOUND)


async def process_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    request = await process_connection(reader)
    logger(f"received {request.method} request on {request.path}")
    response = await process_response(request)
    writer.write(response.byte_response)
    writer.close()


async def process_connection(reader: asyncio.StreamReader) -> HTTPRequest:
    request_bytes = await reader.read(BUFFER_SIZE)
    request = request_bytes.decode()
    start_line, *headers, body_object = request.split(RESPONSE_SEP)
    method, path, http_version = start_line.split(" ")
    if body_object:
        return HTTPRequest(method, path, http_version, headers, body_object)
    return HTTPRequest(method, path, http_version, headers)


async def main():
    server = await asyncio.start_server(process_client, host="localhost", port=PORT)
    logger(f"created server on localhost:{PORT}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-d", "--directory", help="the directory to be mounted")
    args = parser.parse_args()

    directory: Directory = None
    if args.directory:
        directory = Path(args.directory)

    asyncio.run(main())
