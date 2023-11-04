import asyncio
from pathlib import Path
import time
from argparse import ArgumentParser
from http import HTTPStatus

from http_types import RESPONSE_SEP, Directory, HTTPRequest, HTTPResponse

PORT = 4221
BUFFER_SIZE = 2048


def logger(string: str):
    log_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"{log_time} | {string}")


async def process_response(request: HTTPRequest) -> HTTPResponse:
    status = HTTPStatus.OK
    content: str | None = None
    content_type: str | None = None

    match request.path:
        case "/":
            pass

        case path if path.startswith("/echo/"):
            content = path.split("/echo/")[1]

        case "/user-agent":
            headers = await request.request_headers()
            content = headers["User-Agent"]

        case path if path.startswith("/files/"):
            status = HTTPStatus.NOT_FOUND
            filename = path.split("/files/")[1].strip()
            if directory is not None:
                file = directory.joinpath(filename)
                if file.is_file():
                    status = HTTPStatus.OK
                    content = file.read_text()
                    content_type = "application/octet-stream"

        case _:
            status = HTTPStatus.NOT_FOUND

    return HTTPResponse(content=content, status=status, content_type=content_type)


async def process_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    request = await process_connection(reader)
    logger(f"received {request.method} request on {request.path}")
    response = await process_response(request)
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
    logger(f"created server on localhost:{PORT}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-d", "--directory", dest="directory")

    args = parser.parse_args()
    directory: Directory = Path(args.directory)

    asyncio.run(main())
