# aes-modes

对称加密的工作模式。这份材料说明 AES 的 ECB、CBC、CTR 为什么都叫加密、密文看起来却不一样，以及一个没有完整性校验的登录令牌为什么还能被改写。

Modes of operation for a block cipher. These notes explain why AES-ECB, AES-CBC, and AES-CTR all count as encryption and still leave different traces, and why a login token with no integrity check can be rewritten.

## 要回答的问题

1. **歌词里的 ECB。** 同一段歌词有三份 Base64 密文。哪一份是 AES-ECB，依据是什么。
2. **歌词里的 CTR。** 哪一份是 AES-CTR。这一份不用写程序，对照明文长度和填充就能看出来。剩下那一份是 AES-CBC。
3. **像素图。** `ciphertext-sprites/` 里有 12 张 48×48 的灰度图，每种模式四张，密钥相同。判断每一张用的是哪种模式。
4. **CTR 令牌。** 把服务器发出的 `guest` 令牌改成 `admin`，再改成 `super_admin`。
5. **ECB 令牌。** 同样把角色改成 `admin` 或 `super_admin`，用的是分组可以剪贴这一条。
6. **ECB 口令。** 在允许 `&` 的弱接口上，逐字节读出服务器的 `code`。
7. **CBC 口令。** 服务器会把填充错误说出来。用这个回显，从最后一字节往前读出 `code`。

## Questions

1. **ECB in the lyrics.** Three Base64 ciphertexts encrypt the same lyrics. Which one is AES-ECB, and why.
2. **CTR in the lyrics.** Which one is AES-CTR. No program is required: compare the plaintext length with padding. The file that remains is AES-CBC.
3. **Sprites.** `ciphertext-sprites/` holds twelve 48×48 grayscale images, four per mode, one shared key. Name the mode of each image.
4. **CTR token.** Turn a `guest` token from the server into `admin`, then into `super_admin`.
5. **ECB token.** Same role change, using the fact that blocks can be cut and pasted.
6. **ECB code.** On the weak interface that allows `&`, read the server’s `code` one byte at a time.
7. **CBC code.** The server reports padding failures. Use that reply to read `code` from the last byte backward.

下文的文件名、块重复和图片编号都指这份目录里的材料。

File names, repeated blocks, and image numbers below refer to the files in this directory.

## 三种工作模式

明文是字节串。AES 每次吃 16 字节，叫一个分组。密钥长 16 字节。三种模式的差别不在 AES 本身，而在分组之间怎么接。

### ECB

每个分组单独加密，前后分组互不影响。同一密钥下，相同的 16 字节明文永远变成相同的 16 字节密文。歌词里反复出现的句子、图片里成片相同的像素，都会在密文里原样重复。

长度必须是 16 的倍数。这里用 PKCS#7：缺几个字节就补几个数值等于缺口的字节。已经对齐时仍再补一整组 16 个 `0x10`，否则解密无法区分「刚好对齐」和「末尾真的是填充」。

### CBC

加密前，当前明文分组先与上一组密文异或。第一组没有上一组密文，就与初始化向量 IV 异或。因此相同的明文分组，只要前面不同，密文就不同。一份密文内部几乎不会出现重复分组。

IV 若全是 0，第一组密文等于 ECB 对第一组明文的加密。链式从第二组才开始分叉。CBC 同样要 PKCS#7 填充。

### CTR

AES 不去加密明文。它加密的是「nonce 拼上计数器」，得到一条密钥流，再与明文逐字节异或。密文长度等于明文长度，不填充。同一明文出现两次，计数器已经前进，密文并不重复。

把任意字节串再异或进密文，等于把同一串异或进明文。没有完整性校验时，改密文就是改明文。

## The three modes

Plaintext is a byte string. AES consumes 16 bytes at a time; that slice is one block. The key is 16 bytes. The three modes differ in how blocks are joined, not in AES itself.

### ECB

Each block is encrypted on its own. Under one key, the same 16 plaintext bytes always become the same 16 ciphertext bytes. A repeated line in the lyrics, or a flat region in an image, is repeated in the ciphertext.

The length must be a multiple of 16. PKCS#7 fills the gap with bytes whose value equals the gap. A plaintext that is already aligned still receives a full extra block of sixteen `0x10` bytes, so decryption can tell padding from real data.

### CBC

Before encryption, the current plaintext block is XORed with the previous ciphertext block. The first block has no previous ciphertext, so it is XORed with an IV. Identical plaintext blocks produce different ciphertext once their prefixes differ. A single ciphertext almost never repeats a block.

If the IV is all zeros, the first ciphertext block equals the ECB encryption of the first plaintext block. The chain diverges from the second block. CBC uses PKCS#7 as well.

### CTR

AES does not encrypt the plaintext. It encrypts a nonce concatenated with a counter, producing a keystream that is XORed with the plaintext one byte at a time. The ciphertext has the same length as the plaintext. There is no padding. A repeated plaintext does not repeat in the ciphertext, because the counter has moved.

XORing any byte string into the ciphertext XORs that same string into the plaintext. Without an integrity check, editing the ciphertext edits the plaintext.

## 怎样把三份歌词对上号

明文是 `lyrics/lyrics-plaintext.txt`，ASCII，2896 字节。2896 能被 16 整除，所以 ECB 和 CBC 会多出一整组填充，密文是 2912 字节。CTR 不填充，密文仍是 2896 字节。Base64 把这个差距显示成文件长短：短的那份是 3864 个字符，两份长的是 3884 个字符。

| 文件 | 模式 | 依据 |
| --- | --- | --- |
| `lyrics-ciphertext1.txt` | CTR | 解码后 2896 字节，和明文一样长，没有 PKCS#7 的额外一组 |
| `lyrics-ciphertext3.txt` | ECB | 解码后 2912 字节，而且有重复的 16 字节分组，重复位置和歌词里的重复句对齐 |
| `lyrics-ciphertext2.txt` | CBC | 同样是 2912 字节，181 个有效分组里没有重复。第一组和 ECB 的第一组相同，因为 IV 全 0，第一组还没开始链接 |

歌词里同一句 ` (bumpin' that)` 会落在相同的 16 字节边界上。ECB 把这些分组收成同一段密文，出现四次、三次、两次。CBC 和 CTR 的分组表里没有这种重复。

## How the three lyric files are told apart

The plaintext is `lyrics/lyrics-plaintext.txt`, ASCII, 2896 bytes. 2896 is a multiple of 16, so ECB and CBC gain one full padding block and the ciphertext is 2912 bytes. CTR does not pad, so the ciphertext stays 2896 bytes. Base64 shows that gap as file length: the short file is 3864 characters, and the two long files are 3884.

| File | Mode | Why |
| --- | --- | --- |
| `lyrics-ciphertext1.txt` | CTR | Decodes to 2896 bytes, the plaintext length, with no extra PKCS#7 block |
| `lyrics-ciphertext3.txt` | ECB | Decodes to 2912 bytes and repeats 16-byte blocks at the same places the lyrics repeat a line |
| `lyrics-ciphertext2.txt` | CBC | Also 2912 bytes, and none of the 181 content blocks repeats. Its first block equals ECB’s first block, because the IV is all zeros and chaining has not started |

The line ` (bumpin' that)` lands on the same 16-byte boundary more than once. ECB collapses those blocks to one ciphertext block, repeated four, three, or two times. CBC and CTR have no such repeat.

## 怎样把十二张图对上号

每张图是 48×48 灰度，一行 48 字节，正好三组，全文 2304 字节，不填充。十二张用同一条密钥。CBC 的 IV 和 CTR 的 nonce 都是全 0，所以四张 CTR 共用同一条密钥流。

| 模式 | 图片编号 | 依据 |
| --- | --- | --- |
| ECB | 0、4、6、9 | 图内有重复分组。大块相同像素变成大块相同密文，轮廓还在。这四张的 PNG 也比其余的小 |
| CTR | 2、3、5、10 | 图内几乎不重复。两张互异或是两张明文的异或，相邻像素仍相关。相同明文分组即使中间隔着别的分组，密文仍然相同 |
| CBC | 1、7、8、11 | 图内不重复，两张互异或像噪声。8 和 11 的前 11 个分组相同，从第一处不同开始后面全部分叉，这是链接，不是密钥流 |

ECB 看单张就够。CTR 和 CBC 单张都像噪声，要两张放在一起看：密钥流相同，异或能消掉密钥流；链接从第一个不同分组起就对不齐。

## How the twelve images are told apart

Each image is 48×48 grayscale. A row is 48 bytes, exactly three blocks, 2304 bytes in all, with no padding. All twelve use one key. The CBC IV and the CTR nonce are all zeros, so the four CTR images share one keystream.

| Mode | Images | Why |
| --- | --- | --- |
| ECB | 0, 4, 6, 9 | Blocks repeat inside the image. Flat pixels stay flat in the ciphertext, and the outline remains. These four PNGs are also smaller than the rest |
| CTR | 2, 3, 5, 10 | Almost no repeat inside one image. The XOR of two images is the XOR of two plaintexts, so neighboring pixels still correlate. Equal plaintext blocks match in the ciphertext even when a different block sits between them |
| CBC | 1, 7, 8, 11 | No internal repeat, and the XOR of two images looks like noise. Images 8 and 11 share their first 11 blocks, then diverge at the first difference and never meet again. That is chaining, not a keystream |

ECB is visible in one image. CTR and CBC each look like noise alone, so they are compared in pairs: a shared keystream cancels under XOR, and a chain splits at the first block that differs.

## 登录令牌

服务器把一条 ASCII 串加密后交给客户端：

```text
name=<name>&pwd=<pwd>&role=guest&code=<code>
```

`code` 是 24 个随机字节的 Base64，32 个字符，只有服务器知道。客户端以后交回密文、名字和口令。服务器解密，核对名字、口令和 `code`，然后返回 `role`。

普通接口拒绝名字或口令里的 `&`。`generate_guest_token_weak` 不拒绝。CBC 和 CTR 每次发一个新的 IV 或 nonce。ECB 没有。解密出错时，服务器把错误种类返回去，填充错误因此可以被看见。

四件事都不用密钥。

- **CTR 改角色。** 已知明文的那段密钥流是密文异或明文。`guest` 和 `admin` 都是 5 字节，在 `role=` 上异或两者之差即可。`super_admin` 多 6 字节。把口令事先加长 6 字节，改写时再缩回去，`&code=` 和后面的 `code` 仍落在原来的密钥流上，未知的 `code` 密文原样拷走。
- **ECB 改角色。** 分组互相独立，可以剪下来重排。`role=super_admin` 正好 16 字节，而且不含 `&`，可以放进口令里加密成一个分组，再贴到真实令牌里 `code` 分组的前面。`admin` 更短，用同样的对齐，让含有 `admin` 的分组接上模板里的 `&role=` 或替换含有 `guest` 的那一组。
- **ECB 读 code。** 弱接口允许用 `&` 和长度把未知的下一字节顶到某个分组的最后一个位置。其余字节已知。对这个字节试遍可打印字符，哪一次加密出的分组和真实令牌的那一组相同，那个字符就是 `code` 的下一字节。然后滑一个字节，重复。
- **CBC 读 code。** 改倒数第二组密文的最后一个字节，直到服务器不再报告填充错误。那时明文最后一字节是 `0x01`。异或关系把它还原成原来的最后一字节，也就是 `code` 的最后一字符。再伪造长度为 2、3、… 的填充，往前读完 32 个字符。

## The login token

The server encrypts one ASCII string and gives it to the client:

```text
name=<name>&pwd=<pwd>&role=guest&code=<code>
```

`code` is the Base64 of 24 random bytes, 32 characters, known only to the server. The client later returns the ciphertext, the name, and the password. The server decrypts, checks the name, the password, and `code`, and returns `role`.

The ordinary interface rejects `&` in the name or the password. `generate_guest_token_weak` does not. CBC and CTR send a fresh IV or nonce each time. ECB has neither. On a decrypt error the server returns the kind of error, so a padding failure is visible.

None of the four changes needs the key.

- **CTR role.** The keystream on known plaintext is ciphertext XOR plaintext. `guest` and `admin` are both 5 bytes, so XORing their difference into the `role=` field is enough. `super_admin` is 6 bytes longer. Choose a password 6 bytes longer than the one that will be submitted, then shorten it in the forged plaintext, so `&code=` and the code stay on the original keystream. The unknown code ciphertext is copied unchanged.
- **ECB role.** Blocks are independent and can be reordered. `role=super_admin` is exactly 16 bytes and contains no `&`, so it can be placed in a password, encrypted as one block, and pasted in front of the real token’s code blocks. `admin` is shorter; the same alignment puts a block that contains `admin` against the template’s `&role=`, or over the block that contains `guest`.
- **ECB code.** The weak interface allows `&` and a chosen length, which parks the next unknown byte at the end of a block whose other bytes are known. Try every printable character. The guess whose ciphertext block matches the real token is the next character of `code`. Slide one byte and repeat.
- **CBC code.** Change the last byte of the second-to-last ciphertext block until the server stops reporting bad padding. The last plaintext byte is then `0x01`. The XOR relation restores the original last byte, which is the last character of `code`. Forge padding of length 2, 3, … to walk backward through all 32 characters.

## 文件

| 路径 | 内容 |
| --- | --- |
| `a2-cpen442-26w1.pdf` | 说明 |
| `lyrics/lyrics-plaintext.txt` | 歌词明文 |
| `lyrics/lyrics-ciphertext1.txt` | CTR |
| `lyrics/lyrics-ciphertext2.txt` | CBC |
| `lyrics/lyrics-ciphertext3.txt` | ECB |
| `ciphertext-sprites/` | 十二张密文图，`0.png`–`11.png` |
| `utils.py` | 读图、按 ECB / CBC / CTR 加密、显示。CBC 的 IV 和 CTR 的 nonce 都是全 0 |
| `server.py` | 发行并校验登录令牌 |
| `attacker.py` | 四个改写函数留在这里 |
| `tests.py` | 按服务器的返回给这四个函数打分 |
| `question2.py` | 统计歌词密文的重复分组 |
| `submission/` | 解答稿 |

## Files

| Path | Contents |
| --- | --- |
| `a2-cpen442-26w1.pdf` | Handout |
| `lyrics/lyrics-plaintext.txt` | Lyric plaintext |
| `lyrics/lyrics-ciphertext1.txt` | CTR |
| `lyrics/lyrics-ciphertext2.txt` | CBC |
| `lyrics/lyrics-ciphertext3.txt` | ECB |
| `ciphertext-sprites/` | Twelve ciphertext images, `0.png`–`11.png` |
| `utils.py` | Load an image, encrypt with ECB / CBC / CTR, and display it. The CBC IV and the CTR nonce are all zeros |
| `server.py` | Issues and checks login tokens |
| `attacker.py` | The four rewrite functions belong here |
| `tests.py` | Scores those four functions from the server’s reply |
| `question2.py` | Counts repeated blocks in the lyric ciphertexts |
| `submission/` | Write-up |
# AES-Modes
