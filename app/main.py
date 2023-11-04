import asyncio
import time

from http_types import HTTPRequest, RESPONSE_SEP

PORT = 4221
BUFFER_SIZE = 2048


def logger(string: str):
    log_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"{log_time} {string}")


async def process_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    request = await process_connection(reader)
    logger(f"received {request.method} request on {request.path}")
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
    logger(f"created server on localhost:{PORT}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
