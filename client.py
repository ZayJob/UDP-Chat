import socket, threading, time


HOST = socket.gethostbyname(socket.gethostname())
PORT = 0

class Client:
    def __new__(cls,*args, **kwargs):
        """Singleton pattern"""
        
        if not hasattr(cls,'_inst'):
            cls._inst = super(Client, cls).__new__(cls)
        return cls._inst


    def __init__(self, host: str, port: int, name: str, key=8194, host_server="", port_server=9090):
        self.host = host
        self.port = port
        self.name_client = name
        self.key = key
        self.server = (host_server, port_server)
        self.s = None
        self.rT = None
        self.join = False
    
    
    def client_config(self, AddressFamily=None , SocketKind=None) -> None:
        """Confing for setting work client"""
        
        self._configurate_socket(AddressFamily, SocketKind)
        self._configurate_threading()
    
    
    def _configurate_threading(self) -> None:
        """Setting threading"""
        
        self.rT = threading.Thread(target=self._receving_data, args=("RecvThread", self.s))
        self.rT.start()
    
    
    def _configurate_socket(self, AddressFamily, SocketKind) -> None:
        """Setting socket, change UPD on TCP"""
        
        if AddressFamily == None and SocketKind == None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.s = socket.socket(AddressFamily, SocketKind)
            
        self.s.bind((HOST, PORT))
        self.s.setblocking(0)
    
    
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


    def _receving_data(self, name: str, socket) -> None:
        """Receiving data and decrypt for output in terminal"""
        
        while True:
            try:
                while True:
                    data ,address = socket.recvfrom(1024)
                    
                    decrypt_data = self._decrypted(data)
                    print(decrypt_data)
                    
                    time.sleep(0.2)
            except Exception as ex:
                pass



    def _join_server(self) -> None:
        """Send data after entry global chat"""
        
        crypt_data = self._crypted("\nName: {0}  => join chat ")
        self.s.sendto((crypt_data).format(self.name_client).encode("utf-8"), self.server)
        self.join = True
    
    
    def _send_data_to_group(self, data: str, id_group: int) -> None:
        """Send data to server"""
        
        if data != "":
            self.s.sendto(("\nName: {0} :: {1} ").format(self.name_client, data).encode("utf-8"), self.server)
        else:
            print("Incorrect data")


    def _send_data_all_clients(self, data: str) -> None:
        """Send data to server"""
        
        if data != "":
            self.s.sendto(("\nName: {0} :: {1} ").format(self.name_client, data).encode("utf-8"), self.server)
        else:
            print("Incorrect data")


    def _left_server(self) -> None:
        """Send data after exit global chat"""
        
        self.s.sendto(("\nName: {0}  <= left chat ").format(self.name_client).encode("utf-8"), self.server)
    
    
    def _arg_parser(self, data: str) -> int:
        try:
            array_data = data.split(" ")
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


    def _show_groups():
        pass


    def _show_clients(self) -> None: #fix
        """Send commant on server"""
        
        self.s.sendto(("showClients").encode("utf-8"), self.server)
    
    
    def _create_group(self, data: str) -> None:
        """Send commant on server"""
        
        self.s.sendto(("createGroup" + " " + data).encode("utf-8"), self.server)
       


    def start(self) -> None:
        """Stream processing on client"""
        
        self.name_client = self._crypted(self.name_client)
        
        while True:
            if self.join == False:
                self._join_server()
            else:
                try:
                    data = input()
                    
                    id_group, num_action, data = self._arg_parser(data)

                    crypt_data = self._crypted(data)
                    
                    if num_action == 0:
                        self._send_data_all_clients(crypt_data)
                    elif num_action == 1:
                        self._send_data_to_group(crypt_data, id_group)
                    elif num_action == 2:
                        self._create_group(data)
                    elif num_action == 3:
                        self._show_clients()
                    elif num_action == 4:
                        self._show_groups()
                    
                    time.sleep(0.2)
                except Exception as ex:
                    self._left_server()
                    raise
        rT.join()
        self.s.close()


if __name__ == "__main__":
    """Entry point client"""
    
    try:
        print("INIT CLIENT")
        name_client = input("ENTER NAME: ")
        client = Client(HOST, PORT, name_client)
        
        print("CONFIGURATE CLIENT")
        client.client_config()
        
        print("START CLIENT")
        client.start()

    except Exception as ex:
        print("STOP CLIENT - {0}".format(ex))