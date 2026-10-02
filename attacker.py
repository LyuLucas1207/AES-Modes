# File to complete by the students
from typing import Callable
from Crypto.Cipher import AES
# ^^^ These are all the packages/modules you need ^^^

def forge_admin_token_ctr(generate_guest_token: Callable[[str, str], tuple[bytes, bytes]], 
                          read_token: Callable[[bytes, bytes, str, str], str]) -> tuple[bytes, bytes, str, str]:
    name = 'Lucas'
    pwd = '12345678'
    extra = "AAAAAA"
    ciphertext, nonce_or_iv = generate_guest_token(name, pwd + extra)

    requested: bytes = f"name={name}&pwd={pwd + extra}&role=guest".encode('ascii')
    #print(f"req: {requested.hex()}")
    wanted: bytes = f"name={name}&pwd={pwd}&role=super_admin".encode('ascii')
    #print(f"wan: {wanted.hex()}")

    #print(f"req: {requested.decode('ascii')}")
    #print(f"wan: {wanted.decode('ascii')}")

    requested_xor_wanted: bytes = bytes(a ^ b for a, b in zip(requested, wanted))
    #print(f"req_xor_wan: {requested_xor_wanted.hex()}")
    forged = bytearray(ciphertext)
    for i in range(len(requested_xor_wanted)):
        forged[i] = forged[i] ^ requested_xor_wanted[i]
    return bytes(forged), nonce_or_iv, name, pwd

def forge_admin_token_ecb(generate_guest_token: Callable[[str, str], tuple[bytes, bytes]], 
                          read_token: Callable[[bytes, bytes, str, str], str]) -> tuple[bytes, str, str]:
    
    name = 'Lucas'
    pwd = '1234567890abcdef'
    block_size = AES.block_size
    prefix_ct, _ = generate_guest_token(name, pwd)
    """'
    block size: 16
    block1: name=Lucas&pwd=1
    block2: 234567890abcdef&
    """
    useful_block = prefix_ct[:2 * block_size]
    role_ct, _ = generate_guest_token(name, "Xrole=super_admin")
    """
    block size: 16
    block1: name=Lucas&pwd=X
    block2: role=super_admin
    """
    useful_block = useful_block + role_ct[block_size:2 * block_size]
    code_ct, _ = generate_guest_token(name, "123456")
    """
    block size: 16
    block1: name=Lucas&pwd=1
    block2: 23456&role=guest
    block3: &code=xxxxxxxxxx
    """
    useful_block = useful_block + code_ct[2 * block_size:]
    return bytes(useful_block), name, pwd

def guess_code_ecb(generate_guest_token: Callable[[str, str], tuple[bytes, bytes]], 
                   read_token: Callable[[bytes, bytes, str, str], str]) -> str:
    """
    block size: 16 

    real: pwd = 00000 0000000000000000 00000000000000
    block: name=L&pwd=00000
    block: 0000000000000000
    block: 00000000000000&r
    block: ole=guest&code=x    <= block 4
    block: xxxxxx

    fake: pwd = 00000 0000000000000000 0000000000000000 ole=guest&code=y
    block: name=L&pwd=00000
    block: 0000000000000000
    block: 0000000000000000
    block: ole=guest&code=y   <= block 4
    block: &role=guest&code
    block: =xxxxxx

    real: pwd = 00000 0000000000000000 0000000000000 (-1 zero)
    block: name=L&pwd=00000
    block: 0000000000000000
    block: 0000000000000&ro
    block: le=guest&code=Ex    <= block 4, first x already guessed = E
    block: xxxxxx

    fake: pwd = 00000 0000000000000000 000000000000000 ole=guest&code=yy
    block: name=L&pwd=00000
    block: 0000000000000000
    block: 000000000000000o
    block: le=guest&code=Ey   <= block 4, first y already guessed = E
    block: &role=guest&code
    block: =xxxxxx

    only need to compare block 4
    """
    block_size = AES.block_size
    base64_input = 24 # 24 bytes of base64 input
    code_len = base64_input // 3 * 4 # 32 bytes of code

    name = 'L'
    alphabet = (
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        'abcdefghijklmnopqrstuvwxyz'
        '0123456789'
        '+/'
    )


    real_pwd = "00000" "0000000000000000" "00000000000000"
    fake_pwd = "00000" "0000000000000000" "0000000000000000" "ole=guest&code="
    code = ''
    for _ in range(code_len):
        ref_ct, _ = generate_guest_token(name, real_pwd)
        ref_block = ref_ct[3 * block_size:4 * block_size] # block 4, only need to compare this block

        found = ''
        for guess in alphabet:
            guess_ct, _ = generate_guest_token(name, fake_pwd + guess)
            guess_block = guess_ct[3 * block_size:4 * block_size] # block 4 only need to compare this block
            if guess_block == ref_block:
                found = guess
                break
        code += found
        real_pwd = real_pwd[1:]
        fake_pwd = fake_pwd[1:] + found
    return code

def guess_code_cbc(generate_guest_token: Callable[[str, str], tuple[bytes, bytes]], 
                   read_token: Callable[[bytes, bytes, str, str], str]) -> str:
    """
    block size: 16
    name=L, pwd=0000. The prefix is two blocks, the code is the next two.
    64 is a multiple of 16, so PKCS#7 adds one more block of 0x10.
    block1: name=L&pwd=0000&
    block2: role=guest&code=
    block3: xxxxxxxxxxxxxxxx   <= code, first 16
    block4: xxxxxxxxxxxxxxxx   <= code, last 16. last byte is the last code char
    block5: 0x10 * 16           <= padding

              block4[15] = E(Plaintext_block4[15] xor block3[15])
           D(block4[15]) = Plaintext_block4[15] xor block3[15]
    Plaintext_block4[15] = D(block4[15]) xor block3[15]

    only send block3[0:14] block3[15] | block4
    padding need to be 0x10, so we need to guess the last byte of block3[15]
    => D(block4[15]) xor guess_block3[15] = 0x10
                            D(block4[15]) = 0x10 xor guess_block3[15]
                     Plaintext_block4[15] = 0x10 xor guess_block3[15] xor block3[15]

    block size: 16
    name=L, pwd=00000 +1 zero
    64 is a multiple of 16, so PKCS#7 adds one more block of 0x10.
    block1: name=L&pwd=00000
    block2: &role=guest&code
    block3: =xxxxxxxxxxxxxxx   
    block4: xxxxxxxxxxxxxxxx
    block5: x....

              block4[15] = E(Plaintext_block4[15] xor block3[15])
           D(block4[15]) = Plaintext_block4[15] xor block3[15]
    Plaintext_block4[15] = D(block4[15]) xor block3[15]

    only send block3[0:14] block3[15] | block4
    padding need to be 0x10, so we need to guess the last byte of block3[15]
    => D(block4[15]) xor guess_block3[15] = 0x10
                            D(block4[15]) = 0x10 xor guess_block3[15]
                     Plaintext_block4[15] = 0x10 xor guess_block3[15] xor block3[15]
    """
    block_size = AES.block_size
    pwd = '0000'
    name = 'L'
    code_len = 32
    real_code = ''
    wanted = 0x01

    def padding_ok(token: bytes, iv: bytes, pwd: str) -> bool:
        result = read_token(token, iv, name, pwd)
        return 'padding is incorrect' not in result.lower()

    for _ in range(code_len):
        ciphertext, iv = generate_guest_token(name, pwd)
        block3 = bytearray(ciphertext[2 * block_size:3 * block_size])
        block4 = ciphertext[3 * block_size:4 * block_size]
        original_last = block3[-1]

        for guess in range(256):
            block3[-1] = guess
            if not padding_ok(bytes(block3) + block4, iv, pwd):
                continue
            # A longer accidental pad also passes. Flip the byte before it.
            check = bytearray(block3)
            check[-2] ^= 0xff
            if not padding_ok(bytes(check) + block4, iv, pwd):
                continue

            # get the plaintext char
            plain = (wanted ^ guess) ^ original_last

            # put the plaintext char in front, because we are going backward
            real_code = chr(plain) + real_code
            break
        pwd += '0'

    return real_code
