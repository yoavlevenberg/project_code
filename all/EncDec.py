import os
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets
import hashlib





class EncDec:
    """
    A class for Diffie-Hellman key exchange with AES encryption.
    """

    def __init__(self, key):
        self.key = key

    def encrypt(self, message):
        """
        Encrypts the given message using AES encryption.

        :param message: The message to encrypt.
        :return: The IV prepended to the ciphertext.

        The encrypt method takes a plaintext message, applies PKCS7 padding, generates a random IV,
        encrypts the padded message using AES in CBC mode,
        and returns the IV concatenated with the ciphertext
        """

        # Apply PKCS7 padding to the message
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()

        # Generate a random IV
        iv = os.urandom(16)

        # Initialize AES cipher in CBC mode
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt the padded message
        ct = encryptor.update(padded_data) + encryptor.finalize()

        # Return IV prepended to the ciphertext
        return iv + ct

    def decrypt(self, encrypted_message):
        """
        Decrypts the given encrypted message using AES decryption.

        :param encrypted_message: The encrypted message with the IV prepended.
        :return: The decrypted message.
        """

        # Extract the IV from the beginning of the encrypted message
        iv = encrypted_message[:16]
        ct = encrypted_message[16:]

        # Initialize AES cipher in CBC mode with the extracted IV
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the ciphertext
        padded_data = decryptor.update(ct) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()

        # Remove PKCS7 padding
        dec_msg = unpadder.update(padded_data) + unpadder.finalize()
        return dec_msg.decode()

    @staticmethod
    def get_key():
        """
        Generates a Diffie-Hellman key component (public key) and a private key.
        :return: A private key and the corresponding public key.
        """
        # `a` is the private key, and `A` is the public key.
        a = secrets.randbelow(p)  # Generate a random private key.
        print("key---")
        return a, (pow(g, a) % p)  # Return the private key and compute the public key.

    @staticmethod
    def set_key(a, B):
        """
        Generates a shared secret key based on the Diffie-Hellman key exchange protocol.
        :param B: The public key received.
        :param a: Your private key.
        :return: An AES_encryption object initialized with the shared secret key.
        """
        shared_secret = (pow(B, a) % p)
        # Derive a key from the shared secret using SHA-256
        key = hashlib.sha256(str(shared_secret).encode()).digest()
        print("key---")
        return EncDec(key)


# Constants for Diffie-Hellman key exchange
p = 7877  # A prime number for the Diffie-Hellman key exchange
g = 3     # A primitive root modulo p for the Diffie-Hellman key exchange
if __name__ == "__main__":
    # a , b private keys
    # A, B public keys

    c, C = EncDec.get_key()
    d, D = EncDec.get_key()
    key_server = EncDec.set_key(c, D)  # Set up encryption with a derived key.
    key_client = EncDec.set_key(d, C)  # Set up encryption with a derived key.

    original_message = "This is a sfdfffffffffffffffffecret message."
    encrypted_messagee = key_server.encrypt(original_message)
    decrypted_message = key_client.decrypt(encrypted_messagee)

    print(f"Original: {original_message}")
    print(f"Encrypted: {encrypted_messagee}")
    print(f"Decrypted: {decrypted_message}")
