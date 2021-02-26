import socket
import selectors
import threading
import os
import random
import time
import datetime

event = threading.Event()

class Server:
    def __init__(self, host, port):
        self.server_addr = (host, port)
        self.sel = selectors.DefaultSelector()

    def listen(self):
        sock = socket.socket()
        sock.bind(self.server_addr)
        sock.listen(100)
        sock.setblocking(False)
        self.sel.register(sock, selectors.EVENT_READ, self.accept)

        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def accept(self, sock, mask):
        conn, addr = sock.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn, mask):
        data = conn.recv(1000)  # Should be ready
        if data:
            global sum_value 
            sum_value = data.decode()
            event.set()
            print("Recieved value:", sum_value)
        else:
            print('closing', conn)
            self.sel.unregister(conn)
            conn.close()

class Client:
    def __init__(self, node, ip):
        self.sel = selectors.DefaultSelector()
        self.node = os.environ.get('NODE', node)
        self.node_value = os.environ.get('NODE_VALUE', 82)
        self.ip = ip
        
    def secure_sum(self):
        result = 0
        next_number = int(self.ip[-1]) + 1
        next_ip = self.ip[:-1] + str(next_number)
        if int(self.node) == 1:
        # Start of the secure sum at node 1
            start = datetime.datetime.now() 
            r = random.randrange(1000)
            result = r + int(self.node_value)
            self.sock = self.start_connection(next_ip, 4321)
            self.send_value(self.sock, result)
        # Secure sum comes back at node 1
            event.wait()
            final_result = int(sum_value) - r
            end = datetime.datetime.now()
            print("Final result:", final_result)
            print("Duration:", (end - start))
        else:
            # Wait on sum result from other node
            event.wait()
            result = int(sum_value) + int(self.node_value)
            response = os.system("ping -c 1 " + next_ip)
            #print("Response:", response)
            if response == 0:
                self.sock = self.start_connection(next_ip, 4321)
            else:
                self.sock = self.start_connection('10.0.1.2', 4321)
            self.send_value(self.sock, result)

    def start_connection(self, host, port):
        server_addr = (host, port)
        print("starting connection to", server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        return sock

    def send_value(self, sock, value):
        print("Data to send", value)
        data = str(value)
        sock.send(data.encode()) 

def create_server(host, port):
    server = Server(host, port)
    server.listen()

def main():
    host_ip = socket.gethostbyname(socket.gethostname())
    #client_host_ip = os.environ.get('IP','127.0.0.1')
    #host = socket.gethostname()
    #print("Hostname:", host)
    print("Host IP:", host_ip)
    server_thread = threading.Thread(target=create_server, args=(host_ip, 4321))
    server_thread.start()
    time.sleep(20)
    client = Client(1, host_ip)
    client.secure_sum()

if __name__ == '__main__':
    main()