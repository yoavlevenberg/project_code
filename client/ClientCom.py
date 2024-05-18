import socket
import threading
import queue
from all.EncDec import EncDec
from uuid import getnode
from ClientProtocol import ClientProtocol


# ----------------------------------------------------------------------
class ClientComm:
    """
    Handles client-side communication with a server,
    including - connecting, exchanging encryption keys, and message transmission.
    """

    def __init__(self, server_ip, server_port, msg_q):
        """
        Initializes the client communication class.

        :param server_ip: IP address of the server.
        :param server_port: Port number of the server.
        :param msg_q: Queue for storing received messages.
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.msg_q = msg_q
        self.my_socket = None
        self.my_mac = None
        self.key = None
        self.server_is_on = False
        print("gfgfgd")

        # Start the main communication loop in a separate thread.
        threading.Thread(target=self._main_loop).start()

    # ----------------------------------------------------------------------
    def _main_loop(self):
        """
        Connects to the server and continuously listens for incoming messages.
        """
        self.my_socket = socket.socket()
        self._get_mac()
        print(self.my_mac)
        while not self.server_is_on:
            try:
                self.my_socket.connect((self.server_ip, self.server_port))
                self.server_is_on = True


            except Exception as e:
                print("in connection ", str(e))
                self.msg_q.put("server_exist")
                continue
        self.key = self._change_key()  # Exchange encryption keys upon connection.

        # first - send my mac address
        msg2send = ClientProtocol.build_mac(self.my_mac)
        self.send(msg2send)

        while self.server_is_on:
            try:
                # Receive and decrypt messages.
                msg_len = self.my_socket.recv(5).decode()
                msg = self.my_socket.recv(int(msg_len))
                decrypted_msg = self.key.decrypt(msg)
                self.msg_q.put(decrypted_msg)
                print(decrypted_msg)
            except Exception as e:
                print("Error receiving message:", str(e))
                self.my_socket.close()
                self.look_for_server()

    # ----------------------------------------------------------------------
    def look_for_server(self):
        print("in look for server")
        self.server_is_on = False
        self._main_loop()

    # ----------------------------------------------------------------------
    def _change_key(self):
        """
        Handles the exchange of encryption keys with the server.

        :return: The encryption/decryption key object.
        """
        private_key, public_key = EncDec.get_key()  # Generate Diffie-Hellman key pair.
        try:
            # Send public key to server and receive server's public key.
            server_public_key = int(self.my_socket.recv(10).decode())
            self.my_socket.send(str(public_key).zfill(10).encode())
        except Exception as e:
            self.look_for_server()
            print("Error exchanging keys:", str(e))
        else:
            key = EncDec.set_key(private_key, server_public_key)
            print("Key exchange completed.")

        return key

    # ----------------------------------------------------------------------
    def send(self, msg):
        """
        Encrypts and sends a message to the server.

        :param msg: The message to be sent.
        """
        if not self.key:
            print("No encryption key available. Unable to send message.")
            return

        print("len of msg -", len(msg))

        encrypt_msg = self.key.encrypt(msg)
        msg_len = str(len(encrypt_msg)).zfill(5).encode()

        try:
            self.my_socket.send(msg_len + encrypt_msg)
        except Exception as e:
            self.look_for_server()
            print(str(e))

    # ----------------------------------------------------------------------
    def get_ip(self):
        """
        returns ip
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    # ----------------------------------------------------------------------
    def _get_mac(self):
        """
        gets the mac address by the ip address
        :return: the mac address
        """
        self.my_mac = ':'.join(['{:02x}'.format((getnode() >> i) & 0xff) for i in range(0, 8*6, 8)][::-1])

    # ----------------------------------------------------------------------
    def get_mac(self):
        return self.my_mac


if __name__ == "__main__":
    q = queue.Queue()
    server = ClientComm("127.0.0.1", 1234, q)
