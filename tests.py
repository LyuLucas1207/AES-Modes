import attacker
from server import Server
from time import time


def test_forge_token_ctr():

    server = Server('CTR')
    enc_token, nonce_or_iv, name, pwd = attacker.forge_admin_token_ctr(server.generate_guest_token, server.read_token)

    # Grade the result of your attack
    result = server.read_token(enc_token, nonce_or_iv, name, pwd)
    print(f'  Server output from forged token: {result}')
    match result:
        case 'user':
            return 0
        case 'admin':
            return 40
        case 'super_admin':
            return 50
        case _:
            return 0

def test_forge_token_ecb():

    server = Server('ECB')
    enc_token, name, pwd = attacker.forge_admin_token_ecb(server.generate_guest_token, server.read_token)

    # Grade the result of your attack
    result = server.read_token(enc_token, bytes(0), name, pwd)
    print(f'  Server output from forged token: {result}')
    match result:
        case 'user':
            return 0
        case 'admin':
            return 20
        case 'super_admin':
            return 40
        case _:
            return 0
        

def test_guess_code_ecb():

    server = Server('ECB')
    code = attacker.guess_code_ecb(server.generate_guest_token_weak, server.read_token)
    
    # Grade the result of your attack
    print(f'  Server code={server.code}, recovered code={code}')
    if server.code == code:
        return 50
    if len(code)>0 and server.code[0] == code[0]:
        return 25
    return 0



def test_guess_code_cbc():

    server = Server('CBC')
    code = attacker.guess_code_cbc(server.generate_guest_token, server.read_token)
    print(f'  Server code={server.code}, recovered code={code}')
    
    # Grade the result of your attack
    if server.code == code:
        return 50
    if len(code)>0 and server.code[-1] == code[-1]:
        return 25
    return 0




if __name__=="__main__":
    
    t0 = time()
    print(f'CTR forge: {test_forge_token_ctr()}pt, elapsed time {time()-t0:.1}s')
    print(f'ECB forge: {test_forge_token_ecb()}pt, elapsed time {time()-t0:.1}s')

    print(f'ECB code: {test_guess_code_ecb()}pt, elapsed time {time()-t0:.1}s')
    print(f'CBC code: {test_guess_code_cbc()}pt, elapsed time {time()-t0:.1}s')
    