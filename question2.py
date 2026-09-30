"""Question 2.1 Q1: which lyrics ciphertext is AES-ECB?

ECB encrypts each block independently, so identical plaintext blocks
produce identical ciphertext blocks. CBC and CTR do not.
"""

import base64
from collections import Counter
from pathlib import Path

from Crypto.Cipher import AES

HERE = Path(__file__).resolve().parent / "lyrics"
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
#   b"AAAABBBBCCCCDDDD"
def load_ciphertext(path: Path) -> bytes:
    return base64.b64decode(path.read_text().strip())


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


def main() -> None:
    block_size = AES.block_size
    print(f"AES.block_size = {block_size} bytes ({block_size * 8} bits)")
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
        print(f"  ciphertext bytes: {len(data)}")
        print(f"  total blocks: {len(blocks)}")
        print(f"  unique blocks: {len(counts)}")
        print(f"  repeated block types: {len(repeated)}")
        for count, block_hex in repeated:
            print(f"    x{count}  {block_hex}")
        print()


if __name__ == "__main__":
    main()
