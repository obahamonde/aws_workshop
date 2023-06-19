import socket


def aws_parse(items: list) -> dict:
    return {item["Name"]: item["Value"] for item in items}


def gen_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port
