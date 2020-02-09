import socket, time


HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090

class Server:
    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        
        if not hasattr(cls,'_inst'):
            cls._inst = super(Server, cls).__new__(cls)
        return cls._inst

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.clients = []
        self.s = None
    
    def server_config(self, AddressFamily=None , SocketKind=None) -> None: #cahnge in next commit
        """Confing for setting work server"""
        self._configurate_socket()
    
    def _configurate_socket(self, AddressFamily=None , SocketKind=None) -> None:
        """Setting socket, change UPD on TCP"""
        
        if AddressFamily == None and SocketKind == None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.s = socket.socket(AddressFamily, SocketKind)
        
        self.s.bind((self.host, self.port))
    
    def _connection_processing(self, address: tuple) -> bool:
        """Check client on list clients"""
        
        if address not in self.clients:
            self.clients.append(address)
        print("IP - {0} | PORT CLIENT - {1}".format(address[0], address[1]))
        
        return True #change in next commit
        
    def _send_processing(self, data: str, address: tuple) -> None:
        """Send data all clients"""
        
        for client in self.clients:
            if address != client:
                self.s.sendto(data, client)
    
    def _data_processing(self, data: str) -> None:
        """Data processing and output in console"""
        
        server_time = time.strftime("%Y-%M-%D-%H-%M-%S", time.localtime())
        
        print("Time: {0} | Data: {1}".format(server_time, data.decode("utf-8")))
        
    def start(self) -> None:
        """Stream processing on server"""
                
        while True:
            try:
                data, address = self.s.recvfrom(1024)

                connect = self._connection_processing(address)
                
                if connect == True:
                    self._data_processing(data)
                    self._send_processing(data, address)
                else:
                    raise ConnectionError
                
            except Exception as ex:
                raise

        self.s.close()

if __name__ == "__main__":
    """Entry point server"""
    
    try:
        print("INIT SERVER")
        server = Server(HOST, PORT)
        
        print("CONFIGURATE SERVER")
        server.server_config()
        
        print("START SERVER")
        server.start()
    
    except Exception as ex:
        print("STOP SERVER - {0}".format(ex))
