# File to complete by the students
from typing import Callable
from Crypto.Cipher import AES
# ^^^ These are all the packages/modules you need ^^^

def forge_admin_token_ctr(generate_guest_token: Callable[[str, str], tuple[bytes, bytes]], 
                          read_token: Callable[[bytes, bytes, str, str], str]) -> tuple[bytes, bytes, str, str]:
    return bytes(0), bytes(0), 'name', 'pwd'

def forge_admin_token_ecb(generate_guest_token: Callable[[str, str], tuple[bytes, bytes]], 
                          read_token: Callable[[bytes, bytes, str, str], str]) -> tuple[bytes, str, str]:
    return bytes(0), 'name', 'pwd'

def guess_code_ecb(generate_guest_token: Callable[[str, str], tuple[bytes, bytes]], 
                   read_token: Callable[[bytes, bytes, str, str], str]) -> str:
    return ''

def guess_code_cbc(generate_guest_token: Callable[[str, str], tuple[bytes, bytes]], 
                   read_token: Callable[[bytes, bytes, str, str], str]) -> str:
    return ''



