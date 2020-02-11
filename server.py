import socket, time


HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090

class Server:
    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        
        if not hasattr(cls,'_inst'):
            cls._inst = super(Server, cls).__new__(cls)
        return cls._inst


    def __init__(self, host: str, port: int, key=8194):
        self.host = host
        self.port = port
        self.key = key
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

    
    def _connection_processing(self, data: str, address: tuple) -> bool:
        """Check client on list clients"""
        
        address_server = None
        
        data = self._decrypted(data)     
        array_data = data.split(" ")

        if array_data[0] == "\nName:":
            address_server = [address, array_data[1]]

            if address_server not in self.clients:
                self.clients.append(address_server)
            
            
        print("IP - {0} | PORT CLIENT - {1}".format(address[0], address[1]))
        
        return True #change in next commit

    
    def _arg_parser(self, data: str) -> int:
        try:
            array_data = data.decode("utf-8").split()

            if array_data[0] == "createGroup":
                return (None, 2, " ".join(array_data[1::]))
            if array_data[0] == "showClients":
                return (None, 3, " ".join(array_data[1::]))
            if array_data[0] == "showGroups":
                return (None, 4, " ".join(array_data[1::]))
            if int(array_data[0]) >= 0:
                return (int(array_data[0]),1 , " ".join(array_data[1::]))
        except Exception as ex:
            return (None, 0, data)

    
    def _print_data(self, data: str) -> None:
        """Data processing and output in console"""
        
        server_time = time.strftime("%Y-%M-%D-%H-%M-%S", time.localtime())
        
        print("Time: {0} | Data: {1}".format(server_time, data.decode("utf-8")))


    def _crypted(self, data: str) -> str:
        """Crypted string"""
        
        crypt_data = ""
        for char in data:
            crypt_data += chr(ord(char)^self.key)
        return crypt_data

    
    def _decrypted(self, data: str) -> str:
        """Decrypted string"""
        
        decrypt_data = ""
        flag = False
        for char in data.decode("utf-8"):
            if char == ":":
                flag = True
                decrypt_data += char
            elif flag == False or char == " ":
                decrypt_data += char
            else:
                decrypt_data += chr(ord(char)^self.key)
        return decrypt_data


    def _send_data_all_clients(self, data: str, address: tuple) -> None:
        """Send data all clients"""
        
        client_address = [address for address, client_name in self.clients]
        
        for client in client_address:
            if address != client:
                self.s.sendto(data, client)


    def _send_information_about_clients(self, address: tuple) -> None: #fix
        """Send data all clients"""
        
        data = ""
        for client in self.clients:
            data += str(client[0][0])
            data += " "
            data += str(client[0][1])
            data += " "
            data += str(client[1])

        self.s.sendto(data.encode("utf-8"), address)
        

    def _create_group(self, data, address) -> None:
        """Add group to file"""
        with open("Groups.txt", "r") as file_r
            with open("Groups.txt", "w") as file_w:
                pass
    
    
    def start(self) -> None:
        """Stream processing on server"""
                
        while True:
            try:
                data, address = self.s.recvfrom(1024)

                connect = self._connection_processing(data, address)

                if connect == True:
                    self._print_data(data)

                    id_chat, num_action, data = self._arg_parser(data)

                    if num_action == 0:
                        self._send_data_all_clients(data, address)
                    elif num_action == 1:
                        self._create_group(data,address)
                    elif num_action == 2:
                        pass
                    elif num_action == 3:
                        self._send_information_about_clients(address)
                    elif num_action == 4:
                        pass
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
