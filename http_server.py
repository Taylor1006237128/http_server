from socket import *
from select import *
import re


class HttpServer:
    def __init__(self, host="0.0.0.0", port=8000, path="./"):
        self.__HOST = host
        self.__PORT = port
        self.__path = path
        self.__create_socket()
        self.__bind_socket()
        self.__select_server_init()

    @property
    def ADDR(self):
        return self.__ADDR

    def __create_socket(self):
        self.__tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.__tcp_socket.setblocking(False)

    def __bind_socket(self):
        self.__ADDR = (self.__HOST, self.__PORT)
        self.__tcp_socket.bind(self.__ADDR)

    def __select_server_init(self):
        self.__rlist = []
        self.__wlist = []
        self.__xlist = []

    def __select_server(self):
        rs, ws, xs = select(self.__rlist, self.__wlist, self.__xlist)
        for item in rs:
            if item is self.__tcp_socket:
                self.__socket_connect()
            else:
                self.__server_handler(item)

    def __socket_connect(self):
        connect_socket, addr = self.__tcp_socket.accept()
        print("Connect from ", addr)
        connect_socket.setblocking(False)
        self.__rlist.append(connect_socket)

    def __server_handler(self, connect_socket):
        request = connect_socket.recv(1024).decode()
        pattern = r"[A-Z]+\s(/\S*)"
        try:
            info = re.match(pattern, request).group(1)
        except:
            self.__rlist.remove(connect_socket)
            connect_socket.close()
            return
        else:
            self.__send_html(connect_socket, info)

    def __send_html(self, connect_socket, info):
        if info == "/":
            file_name = self.__path + "index.html"
        else:
            file_name = self.__path+info
        try:
            file_read = open(file_name,"rb")
        except:
            response_headers = "HTTP/1.1 404 NOT FOUND\r\n"
            response_headers += "Content-Type:text/html\r\n"
            response_headers += "\r\n"
            response_content = "<h1>Sorry......</h1>"
            response = (response_headers+response_content).encode()
        else:
            response_content = file_read.read()
            response_headers = "HTTP/1.1 404 NOT FOUND\r\n"
            response_headers += "Content-Type:text/html\r\n"
            response_headers += "Content-Length:%d\r\n"%len(response_content)
            response_headers += "\r\n"
            response = response_headers.encode()+response_content
        finally:
            connect_socket.send(response)
            file_read.close()



    def start(self):
        self.__tcp_socket.listen(5)
        print("Listen the port %s" % self.__PORT)
        self.__rlist.append(self.__tcp_socket)
        while True:
            try:
                self.__select_server()
            except KeyboardInterrupt:
                break
        self.__tcp_socket.close()


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 8000
    path = "./static/"
    http_server = HttpServer(host=host, port=port, path=path)
    http_server.start()
