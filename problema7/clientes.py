import socket

def test_proxy():
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.connect(('localhost', 8888))
    
    request = "GET http://example.com/ HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n"
    proxy.send(request.encode())
    
    response = b''
    while True:
        data = proxy.recv(4096)
        if not data: break
        response += data
    
    print(response.decode()[:500])
    proxy.close()

if __name__ == "__main__":
    test_proxy()