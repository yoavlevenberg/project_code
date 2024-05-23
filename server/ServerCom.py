import socket
import threading
import queue
import select
from all.EncDec import EncDec


class ServerCom:
    """
    A server class that handles client connections, key exchanges for encrypted communication, and message forwarding.
    """

    def __init__(self, recv_msg_q):

        """
        Initializes the server.

        :param recv_msg_q: A queue for storing received messages.
        """
        self.my_socket = socket.socket()  # Create a socket object for server
        self.recv_msg_q = recv_msg_q  # Queue to store received messages
        self.open_clients = {}  # Dictionary to keep track of client info: {socket: [ip, key]}

        # Start the main event loop in a separate thread to handle client connections and messages
        threading.Thread(target=self._main_loop).start()

    def _main_loop(self):
        """
        The main loop for the server to accept connections and process incoming messages.
        """
        # Bind the socket to listen to all interfaces on port 1234
        self.my_socket.bind(('0.0.0.0', 1234))
        self.my_socket.listen(3)  # Set the socket to listen mode with a queue of 3

        while True:
            # Use select to handle multiple connections: check for readability
            rlist, wlist, xlist = select.select([self.my_socket] + list(self.open_clients.keys()),
                                                list(self.open_clients.keys()), [], 0.03)

            for this_socket in rlist:
                if this_socket is self.my_socket:
                    # If the server socket is readable, accept the new connection
                    client, addr = self.my_socket.accept()
                    print(f"{addr[0]} - Connected")

                    # Start a new thread to handle the key exchange with the client
                    threading.Thread(target=self._change_key, args=(client, addr[0],)).start()
                    continue

                # Handle data from a client socket
                try:
                    length_of_data = int(this_socket.recv(5).decode())  # Expecting the length of the data
                    data = this_socket.recv(length_of_data)  # Receive the actual data
                    client_key = self.open_clients[this_socket][1]  # get the key using the socket
                    decrypted_data = client_key.decrypt(data)  # Decrypt the received message
                except Exception as e:
                    print("1111main server in server comm ", str(e))
                    self._handle_disconnect(this_socket)
                else:
                    if decrypted_data == "":
                        self._handle_disconnect(this_socket)
                    else:
                        # Put the decrypted data into the received messages queue
                        self.recv_msg_q.put((self.open_clients[this_socket][0], decrypted_data))

    def _handle_disconnect(self, client_socket):
        """
        Handles client disconnection by removing from the open clients list and closing the socket.

        :param client_socket: The socket object of the client to disconnect.
        """
        if client_socket in self.open_clients.keys():
            self.recv_msg_q.put((self.open_clients[client_socket][0], "disconnect"))
            print(f"{self.open_clients[client_socket][0]} - Disconnected")
            del self.open_clients[client_socket]  # Remove the client from the open clients dictionary
            client_socket.close()  # Close the client socket

    def _find_socket_by_ip(self, ip):
        """
        Finds a client socket based on the IP address.

        :param ip: The IP address of the client.
        :return: The socket object for the given IP, or None if not found.
        """
        for i, client_info in self.open_clients.items():
            if client_info[0] == ip:
                return i
        return None

    def send_msg(self, ip, msg):
        """
        Encrypts and sends a message to the client identified by the given IP.

        :param ip: The IP address of the target client.
        :param msg: The message to send.
        """
        print("here")
        client_socket = self._find_socket_by_ip(ip)
        if client_socket:
            client_key = self.open_clients[client_socket][1]  # Get the encryption key
            print("he")
            encrypt_msg = client_key.encrypt(msg)  # Encrypt the message

            # Prepare and send the encrypted message with its length prefixed
            msg_len = str(len(encrypt_msg)).zfill(5).encode()
            try:
                client_socket.send(msg_len + encrypt_msg)
            except Exception as e:
                print("send_msg", str(e))
                self._handle_disconnect(client_socket)

    def _change_key(self, client, ip):
        """
        Handles the key exchange with a client to establish a shared secret for encryption.

        :param client: The client socket.
        :param ip: The IP address of the client.
        """
        private_key_a, public_key_A = EncDec.get_key()  # Generate a new key pair
        try:
            # Send the public key to the client and receive the client's public key
            client.send(str(public_key_A).zfill(10).encode())
            b = int(client.recv(10).decode())
        except Exception as e:
            print("change key failed", str(e))
            client.close()
        else:
            # Generate the shared secret key and store it along with the client's IP
            shared_key = EncDec.set_key(private_key_a, b)
            self.open_clients[client] = [ip, shared_key]
            print(f"{ip} - Finished key exchange")

    def disconnect_client(self, ip):
        """

        :param ip:
        :return:
        """

        sock = self._find_socket_by_ip(ip)
        if sock:
            self._handle_disconnect(sock)
            print(f"{ip} - disconnected by the server ")


# Main program execution
if __name__ == '__main__':
    q = queue.Queue()  # Create a queue for receiving messages
    s = ServerCom(q)  # Instantiate the server with the message queue

    s.send_msg("127.0.0.1", str(input("enter")))
