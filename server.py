import socket
import time


HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090


class Server:
    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if not hasattr(cls, '_inst'):
            cls._inst = super(Server, cls).__new__(cls)
        return cls._inst

    def __init__(self, host: str, port: int, key=8194):
        self.host = host
        self.port = port
        self.key = key
        self.clients = []
        self.s = None

    def server_config(self, AddressFamily=None, SocketKind=None) -> None:
        """Confing for setting work server"""
        self._configurate_socket()

    def _configurate_socket(self, AddressFamily=None, SocketKind=None) -> None:
        """Setting socket, change UPD on TCP"""
        if AddressFamily is None and SocketKind is None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.s = socket.socket(AddressFamily, SocketKind)

        self.s.bind((self.host, self.port))

    def _connection_processing(self, data: str, address: tuple) -> bool:
        """Check client on list clients"""
        address_server = None

        data_decrypt = self._decrypted(data)

        array_data = data_decrypt.split(" ")

        if array_data[0] == "\nName:":
            address_server = [address, array_data[1]]

            if address_server not in self.clients:
                self.clients.append(address_server)

        print("IP - {0} | PORT CLIENT - {1}".format(address[0], address[1]))
        return True

    def _confirmation(self, array_data: list, address: tuple) -> None:
        """Confirm send data"""
        self.s.sendto("Delivered".encode("utf-8"), ("", int(array_data[1])))

    def _arg_parser(self, data: str, address: tuple) -> tuple:
        """Serch args in data, if not find args, generate exceptoin"""
        try:
            array_data = data.decode("utf-8").split(" ")

            if array_data[0] == "OK":
                self._confirmation(array_data, address)
                return (5, None)
            elif array_data[0] == "createGroup":
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

    def _print_data(self, data: str) -> None:
        """Data processing and output in console"""
        server_time = time.strftime("%Y-%M-%D-%H-%M-%S", time.localtime())

        print("Time: {0} | Data: {1}".format(server_time, data.decode("utf-8")))

    def _send_data_all_clients(self, data: str, address: tuple) -> None:
        """Send data all clients"""
        client_address = [address for address, client_name in self.clients]

        for client in client_address:
            if address != client:
                self.s.sendto(data, client)

    def _send_data_about_clients(self, address: tuple) -> None:
        """Send data all clients"""
        data = ""
        for index, client in enumerate(self.clients):
            if address != client[0]:
                data += " ".join([str(index), str(client[0][0]), str(client[0][1]), str(client[1]), "\n"])

        self.s.sendto(data.encode("utf-8"), address)

    def _create_group(self, data: str, address: tuple) -> None:
        """Add group to file"""
        with open("Groups.txt", "r") as file_r:
            array_groups = file_r.readlines()

            with open("Groups.txt", "w") as file_w:
                line = " ".join([("\n" + str(address[1])), data])
                array_groups.append(line)

                file_w.writelines(array_groups)

    def _send_data_about_groups(self, address: tuple) -> None:
        """Send information about group to client"""
        with open("Groups.txt", "r") as file_r:
            array_groups = file_r.readlines()
            data = ""

            for index, group in enumerate(array_groups):
                array_data = group.split(" ")

                if int(array_data[0]) != int(address[1]):
                    continue

                data += " ".join([array_data[1], " ".join(array_data[2:]), "\n"])

            self.s.sendto(data.encode("utf-8"), address)

    def _send_data_to_group(self, data: str, address: tuple) -> None:
        """Send data to group"""
        with open("Groups.txt", "r") as file_r:
            array_groups = file_r.readlines()
            array_data_msg = data.split(" ")

            for index, group in enumerate(array_groups):
                array_data = group.split(" ")

                if int(array_data[0]) == int(address[1]) and array_data[1] == array_data_msg[0]:
                    clients = array_data[2:]

                    for client in clients:
                        msg = " ".join(array_data_msg[1:])

                        if len(clients) == 1:
                            msg = " ".join([msg, str(address[1]), "confirm"])

                        self.s.sendto(msg.encode("utf-8"), ("", int(client)))

    def start(self) -> None:
        """Stream processing on server"""
        while True:
            try:
                data, address = self.s.recvfrom(1024)

                connect = self._connection_processing(data, address)

                if connect:
                    self._print_data(data)

                    num_action, data = self._arg_parser(data, address)

                    if num_action == 0:
                        self._send_data_all_clients(data, address)
                    elif num_action == 1:
                        self._send_data_to_group(data, address)
                    elif num_action == 2:
                        self._create_group(data, address)
                    elif num_action == 3:
                        self._send_data_about_clients(address)
                    elif num_action == 4:
                        self._send_data_about_groups(address)
                    elif num_action == 5:
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
