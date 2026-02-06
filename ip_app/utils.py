# myapp/utils.py

from ping3 import ping

def ping_ip(ip):
    response_time = ping(ip)
    if response_time is not None:
        return f"Response time: {response_time} ms"
    else:
        return "Ping failed"

