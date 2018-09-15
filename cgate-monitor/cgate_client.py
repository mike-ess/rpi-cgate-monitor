import sys
import socket

##############################################################
### CGATE CLIENT
##############################################################

class CGateClient:
    def __init__(self, server_ip_address, portNumber):
        self.server_ip_address = server_ip_address
        self.portNumber = portNumber
        self.s = None

    def open(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.server_ip_address, self.portNumber))
        response = self.s.recv(1024).decode("utf-8")
        return response

    def open_no_listen(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.server_ip_address, self.portNumber))

    def close(self):
        self.s.close()

    def send_receive(self, command):
        command += "\r\n"
        command_bytes = command.encode("utf-8")
        print("sendreceive command: " + command)
        self.s.send(command_bytes)
        print("sendreceive sent!")
        response_bytes = self.s.recv(1024)
        response = response_bytes.decode("utf-8")
        print("sendreceive response: " + response)
        return response;

    def receive(self):
        response_bytes = self.s.recv(1024)
        response = response_bytes.decode("utf-8")
        return response;
