from dataclasses import dataclass
from pathlib import Path
from http import HTTPStatus

RESPONSE_SEP = "\r\n"


Directory = Path | None


@dataclass
class HTTPResponse:
    content: str | None = None
    content_type: str | None = None
    content_length: int | None = None
    status: HTTPStatus = HTTPStatus.NOT_FOUND

    def __post_init__(self):
        if self.content is not None:
            self.content_length = len(self.content)
            if self.content_type is None:
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
