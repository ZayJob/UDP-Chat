import socket
import threading
import time


HOST = socket.gethostbyname(socket.gethostname())
PORT = 0


class Client:
    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if not hasattr(cls, '_inst'):
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

    def client_config(self, AddressFamily=None, SocketKind=None) -> None:
        """Confing for setting work client"""
        self._configurate_socket(AddressFamily, SocketKind)
        self._configurate_threading()

    def _configurate_threading(self) -> None:
        """Setting threading"""
        self.rT = threading.Thread(target=self._receving_data, args=("RecvThread", self.s))
        self.rT.start()

    def _configurate_socket(self, AddressFamily, SocketKind) -> None:
        """Setting socket, change UPD on TCP"""
        if AddressFamily is None and SocketKind is None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.s = socket.socket(AddressFamily, SocketKind)

        self.s.bind((HOST, PORT))
        self.s.setblocking(0)

    def _crypted(self, data: str) -> str:
        """Crypted string, symmetric method"""
        crypt_data = ""
        for char in data:
            crypt_data += chr(ord(char) ^ self.key)
        return crypt_data

    def _decrypted(self, data: str) -> str:
        """Decrypted string, symmetric method"""
        decrypt_data = ""
        flag = False
        for char in data.decode("utf-8"):
            if char == ":":
                flag = True
                decrypt_data += char
            elif not flag or char == " ":
                decrypt_data += char
            else:
                decrypt_data += chr(ord(char) ^ self.key)
        return decrypt_data

    def _receving_data(self, name: str, socket) -> None:
        """Receiving data and decrypt for output in terminal"""
        while True:
            try:
                while True:
                    data, address = socket.recvfrom(1024)

                    decrypt_data = self._decrypted(data)

                    new_decrypt_data = self._confirmation(decrypt_data, address)

                    print(new_decrypt_data)

                    time.sleep(0.2)
            except Exception as ex:
                pass

    def _confirmation(self, decrypt_data: str, address: tuple) -> str:
        """Confirm send data"""
        array_data = decrypt_data.split(" ")

        if array_data[-1] == "confirm":
            self.s.sendto(("OK " + str(array_data[-2])).encode("utf-8"), self.server)

            return " ".join(array_data[:(len(array_data) - 2)])
        return " ".join(array_data)

    def _arg_parser(self, data: str) -> int:
        """Search args in data, if not find args, generate exception"""
        try:
            array_data = data.split(" ")

            if array_data[0] == "createGroup":
                return (2, " ".join(array_data[1::]))
            elif array_data[0] == "showClients":
                return (3, " ".join(array_data[1::]))
            elif array_data[0] == "showGroups":
                return (4, " ".join(array_data[1::]))
            elif array_data[0] == "nameGroup":
                return (1, " ".join(array_data[1::]))
            else:
                raise
        except Exception as ex:
            return (0, data)

    def _join_server(self) -> None:
        """Send data after entry global chat"""
        data_crypted = self._crypted("=> join chat ")
        self.s.sendto(("\nName: {0} " + data_crypted).format(self.name_client).encode("utf-8"), self.server)
        self.join = True

    def _left_server(self) -> None:
        """Send data after exit global chat"""
        self.s.sendto(("\nName: {0}  <= left chat ").format(self.name_client).encode("utf-8"), self.server)

    def _send_data_all_clients(self, data: str) -> None:
        """Send data to server"""
        if data != "":
            self.s.sendto(("\nName: {0} :: {1} ").format(self.name_client, data).encode("utf-8"), self.server)
        else:
            print("Incorrect data")

    def _show_groups(self) -> None:
        """Send command on server"""
        self.s.sendto(("showGroups").encode("utf-8"), self.server)

    def _show_clients(self) -> None:
        """Send command on server"""
        self.s.sendto(("showClients").encode("utf-8"), self.server)

    def _create_group(self, data: str) -> None:
        """Send command on server"""
        self.s.sendto(("createGroup" + " " + data).encode("utf-8"), self.server)

    def _send_data_to_group(self, data: str) -> None:
        """Send commant on server"""
        self.s.sendto(("nameGroup" + " " + data).encode("utf-8"), self.server)

    def start(self) -> None:
        """Stream processing on client"""
        self.name_client = self._crypted(self.name_client)

        while True:
            if not self.join:
                self._join_server()
            else:
                try:
                    data = input()

                    num_action, data = self._arg_parser(data)

                    crypt_data = self._crypted(data)

                    if num_action == 0:
                        self._send_data_all_clients(crypt_data)
                    elif num_action == 1:
                        self._send_data_to_group(data)
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
