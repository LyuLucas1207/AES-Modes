import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def load_image(path: str) -> bytes:
    img = Image.open(path).convert("L") # Convert to grayscale
    array = np.array(img, dtype=np.uint8)
    img_bytes = array.flatten().tobytes()
    return img_bytes


def encrypt_bytes(plaintext_bytes: bytes, key: bytes, mode: str, padding: bool = False) -> bytes:
    assert mode in ('ECB', 'CBC', 'CTR')
    if mode in ("ECB", "CBC"):
        if not padding:
            assert len(plaintext_bytes) % AES.block_size == 0
        else:
            plaintext_bytes = pad(plaintext_bytes, AES.block_size)
    
    match mode:
        case 'ECB':
            cipher = AES.new(key, AES.MODE_ECB)
            return cipher.encrypt(plaintext_bytes)
        case 'CBC':
            iv = bytes(16) # All-zero
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            return cipher.encrypt(plaintext_bytes)
        case 'CTR':
            nonce = bytes(8) # All-zero
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
            return cipher.encrypt(plaintext_bytes)


def show_image(img_bytes: bytes):
    img = np.frombuffer(img_bytes, dtype=np.uint8)
    img = img.reshape((48, 48))
    img = Image.fromarray(img, mode='L')
    plt.imshow(np.array(img), cmap='gray')
    plt.show()


def save_img(path: str, img_bytes: bytes):
    img = np.frombuffer(img_bytes, dtype=np.uint8)
    img = img.reshape((48, 48))
    img = Image.fromarray(img, mode='L')
    img.save(path)