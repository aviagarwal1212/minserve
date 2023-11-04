from dataclasses import dataclass
from http import HTTPStatus

RESPONSE_SEP = "\r\n"


@dataclass
class HTTPResponse:
    content: str | None = None
    content_type: str | None = None
    content_length: int | None = None
    status: HTTPStatus = HTTPStatus.NOT_FOUND

    async def __post_init__(self):
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


HTTPHeaders = dict[str, str]


@dataclass
class HTTPRequest:
    method: str
    path: str
    http_version: str
    headers: list[str]

    async def request_headers(self) -> HTTPHeaders:
        header_dict: HTTPHeaders = {}
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