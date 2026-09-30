from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64



class Server():

    def __init__(self, mode_of_operation: str = 'ECB'):
        self.key = get_random_bytes(AES.block_size)
        self.code = base64.b64encode(get_random_bytes(24)).decode('ascii')
        self.mode = mode_of_operation


    def _encrypt(self, plaintext: bytes) -> tuple[bytes, bytes]:
        """Encrypts the plaintext with AES, returning ciphertext and nonce/iv."""

        match self.mode:
            case 'ECB':
                cipher = AES.new(self.key, AES.MODE_ECB)
                ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
                return ciphertext, bytes(0)
            case 'CBC':
                iv = get_random_bytes(16)
                cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
                ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
                return ciphertext, iv
            case 'CTR':
                nonce = get_random_bytes(8)
                cipher = AES.new(self.key, AES.MODE_CTR, nonce=nonce)
                ciphertext = cipher.encrypt(plaintext) # No padding needed in CTR
                return ciphertext, nonce
            case _:
                raise ValueError('Unknown mode of operation')            

    def _decrypt(self, ciphertext: bytes, nonce_or_iv: bytes = bytes(0)) -> bytes:
        """Decrypts the ciphertext with AES, returning plaintext."""

        match self.mode:
            case 'ECB':
                cipher = AES.new(self.key, AES.MODE_ECB)
                plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
                return plaintext
            case 'CBC':
                cipher = AES.new(self.key, AES.MODE_CBC, iv=nonce_or_iv)
                plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
                return plaintext
            case 'CTR':
                cipher = AES.new(self.key, AES.MODE_CTR, nonce=nonce_or_iv)
                plaintext = cipher.decrypt(ciphertext) # No unpadding needed in CTR
                return plaintext
            case _:
                raise ValueError('Unknown mode of operation')   


    def generate_guest_token(self, name: str, pwd: str) -> tuple[bytes, bytes]:
        """Receives name and password strings, and returns an encrypted user token."""
        if '&' in name or '&' in pwd:
            return bytes(0), bytes(0)
        token_plaintext = f'name={name}&pwd={pwd}&role=guest&code={self.code}' # generate token
        ciphertext, nonce_or_iv = self._encrypt(token_plaintext.encode('ascii'))
        return ciphertext, nonce_or_iv

    def generate_guest_token_weak(self, name: str, pwd: str) -> tuple[bytes, bytes]:
        """Receives name and password strings, and returns an encrypted user token."""
        # No input sanitization (allows &)
        token_plaintext = f'name={name}&pwd={pwd}&role=guest&code={self.code}' # generate token
        ciphertext, nonce_or_iv = self._encrypt(token_plaintext.encode('ascii'))
        return ciphertext, nonce_or_iv
    
    def read_token(self, enc_token: bytes, nonce_or_iv: bytes = bytes(0), name: str = '', pwd: str = '') -> str:
        """Process an encrypted token and, if correct, returns the role in the token."""
        
        try:
            plaintext_token = self._decrypt(enc_token, nonce_or_iv).decode('ascii')

            data = {kv.split('=')[0]: kv.split('=')[1] for kv in plaintext_token.split('&')}
            assert 'name' in data
            assert 'pwd' in data
            assert 'role' in data
            assert 'code' in data
            if data['name'] != name:
                return 'wrong name'
            if data['pwd'] != pwd:
                return 'wrong pwd' # Incorrect password
            elif data['code'] != self.code:
                return 'wrong code' # Incorrect server code
            else:
                return data['role'] # Returning role
        except Exception as e:
            if "Padding is incorrect" in str(e):
                return f'incorrect padding {str(e)}'
            elif "Decrypt error" in str(e):
                return f'decrypt error {str(e)}'
            else:
                return f'other error {str(e)}'