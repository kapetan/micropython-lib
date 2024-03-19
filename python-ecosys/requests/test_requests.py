import io
import sys


class Socket:
    def __init__(self):
        self._write_buffer = io.BytesIO()
        self._read_buffer = io.BytesIO(b"HTTP/1.0 200 OK\r\n\r\n")

    def connect(self, address):
        pass

    def write(self, buf):
        self._write_buffer.write(buf)

    def readline(self):
        return self._read_buffer.readline()


class usocket:
    AF_INET = 2
    SOCK_STREAM = 1
    IPPROTO_TCP = 6

    @staticmethod
    def getaddrinfo(host, port, af=0, type=0, flags=0):
        return [(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP, "", ("127.0.0.1", 80))]

    def socket(af=AF_INET, type=SOCK_STREAM, proto=IPPROTO_TCP):
        return Socket()


sys.modules["usocket"] = usocket
import requests


def test_simple_get():
    response = requests.request("GET", "http://example.com")

    assert response.raw._write_buffer.getvalue() == (
        b"GET / HTTP/1.0\r\n"
        + b"Host: example.com\r\n"
        + b"Connection: close\r\n\r\n")


def test_get_auth():
    response = requests.request("GET", "http://example.com",
        auth=("test-username", "test-password"))

    assert response.raw._write_buffer.getvalue() == (
        b"GET / HTTP/1.0\r\n"
        + b"Authorization: Basic dGVzdC11c2VybmFtZTp0ZXN0LXBhc3N3b3Jk\r\n"
        + b"Host: example.com\r\n"
        + b"Connection: close\r\n\r\n")


def test_get_custom_header():
    response = requests.request("GET", "http://example.com",
        headers={"User-Agent": "test-agent"})

    assert response.raw._write_buffer.getvalue() == (
        b"GET / HTTP/1.0\r\n"
        + b"Host: example.com\r\n"
        + b"Connection: close\r\n"
        + b"User-Agent: test-agent\r\n\r\n")


def test_post_json():
    response = requests.request("GET", "http://example.com", json="test")

    assert response.raw._write_buffer.getvalue() == (
        b"GET / HTTP/1.0\r\n"
        + b"Host: example.com\r\n"
        + b"Content-Type: application/json\r\n"
        + b"Content-Length: 6\r\n"
        + b"Connection: close\r\n\r\n"
        + b"\"test\"")


def test_post_chunked_data():
    def chunks():
        yield "test"

    response = requests.request("GET", "http://example.com", data=chunks())

    assert response.raw._write_buffer.getvalue() == (
        b"GET / HTTP/1.0\r\n"
        + b"Host: example.com\r\n"
        + b"Transfer-Encoding: chunked\r\n"
        + b"Connection: close\r\n\r\n"
        + b"4\r\ntest\r\n"
        + b"0\r\n\r\n")


def test_overwrite_get_headers():
    response = requests.request("GET", "http://example.com",
        headers={"Connection": "keep-alive", "Host": "test.com"})

    assert response.raw._write_buffer.getvalue() == (
        b"GET / HTTP/1.0\r\n"
        + b"Host: test.com\r\n"
        + b"Connection: keep-alive\r\n\r\n")


def test_overwrite_post_json_headers():
    response = requests.request("GET", "http://example.com",
        json="test",
        headers={"Content-Type": "text/plain", "Content-Length": "10"})

    assert response.raw._write_buffer.getvalue() == (
        b"GET / HTTP/1.0\r\n"
        + b"Host: example.com\r\n"
        + b"Connection: close\r\n"
        + b"Content-Length: 10\r\n"
        + b"Content-Type: text/plain\r\n\r\n"
        + b"\"test\"")


def test_overwrite_post_chunked_data_headers():
    def chunks():
        yield "test"

    response = requests.request("GET", "http://example.com",
        data=chunks(),
        headers={"Content-Length": "4"})

    assert response.raw._write_buffer.getvalue() == (
        b"GET / HTTP/1.0\r\n"
        + b"Host: example.com\r\n"
        + b"Connection: close\r\n"
        + b"Content-Length: 4\r\n\r\n"
        + b"test")


test_simple_get()
test_get_auth()
test_get_custom_header()
test_post_json()
test_post_chunked_data()
test_overwrite_get_headers()
test_overwrite_post_json_headers()
test_overwrite_post_chunked_data_headers()
