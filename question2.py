"""Question 2.1 Q1: which lyrics ciphertext is AES-ECB?

ECB encrypts each block independently, so identical plaintext blocks
produce identical ciphertext blocks. CBC and CTR do not.
"""

import base64
from collections import Counter
from pathlib import Path

from Crypto.Cipher import AES

HERE = Path(__file__).resolve().parent / "lyrics"

OUTPUT_PATH = HERE / "output"

FILES = [
    "lyrics-ciphertext1.txt",
    "lyrics-ciphertext2.txt",
    "lyrics-ciphertext3.txt",
]


# 读取 Base64 文本文件，解码成 AES 密文字节。
# 作业文件里存的是 Base64 字符串，不是原始密文，不能按字符切块。
# Read a Base64 text file and return the decoded AES ciphertext bytes.
# The assignment files store Base64 text, not raw ciphertext bytes.
#
# 输入 example / input example:
#   path 指向的文件内容 / file contents:
#   QUFBQUJCQkJDQ0NDRERERA==
# 输出 example / output example:
#   返回值 / return value:
#   b"AAAABBBBCCCCDDDD"
#   同时写入 / also writes:
#   lyrics/output/lyrics-ciphertext1.txt
#   41414141424242424343434344444444
#   每行是一个 16-byte 块的 hex，所以编辑器能打开。
#   Each line is the hex of one 16-byte block, so a text editor can open it.
def load_ciphertext(path: Path) -> bytes:
    ciphertext = base64.b64decode(path.read_text().strip())
    lines = [
        ciphertext[i : i + AES.block_size].hex()
        for i in range(0, len(ciphertext), AES.block_size)
    ]
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    (OUTPUT_PATH / path.name).write_text("\n".join(lines) + "\n")
    return ciphertext


# 把密文字节按 AES 块长切开。ECB 下每一块单独加密，所以后面要按块比较是否相同。
# Split ciphertext bytes into blocks of block_size. ECB encrypts each block
# on its own, so later we compare blocks for exact repeats.
#
# 输入 example / input example:
#   data = b"AAAABBBBCCCCDDDD"
#   block_size = 4
# 输出 example / output example:
#   [b"AAAA", b"BBBB", b"CCCC", b"DDDD"]
def split_blocks(data: bytes, block_size: int) -> list[bytes]:
    return [data[i : i + block_size] for i in range(0, len(data), block_size)]


# 把明文按 16 bytes 切块，每块写一行到 output。
# 块里面的换行写成 \n，这样编辑器里仍然是一行一块。
# Split the plaintext into 16-byte blocks, one block per output line.
# A newline inside a block is written as \n so the block stays on one line.
#
# 输入 example / input example:
#   lyrics/lyrics-plaintext.txt 的开头 / start of the file:
#   Bumpin' that, bumpin' that, bumpin' that, bumpin' that
# 输出 example / output example:
#   lyrics/output/lyrics-plaintext.txt:
#   Bumpin' that, bu
#   mpin' that, bump
#   in' that, bumpin
#   ' that\nBumpin' t
def write_plaintext_blocks(path: Path) -> None:
    data = path.read_bytes()
    lines = [
        block.decode("ascii").encode("unicode_escape").decode("ascii")
        for block in split_blocks(data, AES.block_size)
    ]
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    (OUTPUT_PATH / path.name).write_text("\n".join(lines) + "\n")


def main() -> None:
    block_size = AES.block_size
    print(f"AES.block_size = {block_size} bytes ({block_size * 8} bits)")
    print()

    plaintext_path = HERE / "lyrics-plaintext.txt"
    write_plaintext_blocks(plaintext_path)
    print(f"plaintext blocks: {OUTPUT_PATH / plaintext_path.name}")
    print()

    for name in FILES:
        file_path = HERE / name
        data = load_ciphertext(file_path)
        blocks = split_blocks(data, block_size)
        counts = Counter(blocks)
        repeated = sorted(
            ((count, block.hex()) for block, count in counts.items() if count > 1),
            reverse=True,
        )

        print(name)
        print(f"  decoded file: {OUTPUT_PATH / name}")
        print(f"  ciphertext bytes: {len(data)}")
        print(f"  total blocks: {len(blocks)}")
        print(f"  unique blocks: {len(counts)}")
        print(f"  repeated block types: {len(repeated)}")
        for count, block_hex in repeated:
            print(f"    x{count}  {block_hex}")
        print()


if __name__ == "__main__":
    main()
