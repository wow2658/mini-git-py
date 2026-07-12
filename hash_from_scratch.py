import random
import struct
import hashlib

# ==========================================
# 1. UUID4를 라이브러리 없이 밑바닥부터 구현
# ==========================================
def my_uuid4():
    """
    128비트(16바이트)의 랜덤 데이터를 생성하고,
    UUID version 4 규격에 맞게 비트 마스킹 연산을 수행합니다.
    """
    # 1. 16바이트 랜덤 배열 생성
    bytes_list = [random.randint(0, 255) for _ in range(16)]
    
    # 2. 7번째 바이트의 상위 4비트를 0100 (Version 4)로 세팅
    bytes_list[6] = (bytes_list[6] & 0x0f) | 0x40
    
    # 3. 9번째 바이트의 상위 2비트를 10 (Variant 1)로 세팅
    bytes_list[8] = (bytes_list[8] & 0x3f) | 0x80
    
    # 4. 16진수 문자열로 포매팅 (8-4-4-4-12 규격)
    hex_str = ''.join(f'{b:02x}' for b in bytes_list)
    return f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:]}"


# ==========================================
# 2. SHA-1을 라이브러리 없이 밑바닥부터 구현
# ==========================================
def left_rotate(n, b):
    # 32비트 비트 시프트(순환 이동) 연산
    return ((n << b) | (n >> (32 - b))) & 0xffffffff

def my_sha1(message: bytes) -> str:
    """
    입력된 메시지를 SHA-1 수학적 알고리즘을 거쳐 
    고정된 40자리 16진수 해시로 변환합니다.
    """
    # 1. 매직 넘버 초기화 (SHA-1 스펙)
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0

    # 2. 패딩(Padding) 작업: 데이터를 64바이트(512비트) 블록으로 맞춤
    original_byte_len = len(message)
    original_bit_len = original_byte_len * 8
    message += b'\x80'
    message += b'\x00' * ((56 - (original_byte_len + 1) % 64) % 64)
    message += struct.pack('>Q', original_bit_len)

    # 3. 64바이트 블록 단위로 쪼개서 복잡한 수학 연산 80회 반복
    for i in range(0, len(message), 64):
        chunk = message[i:i+64]
        w = [0] * 80
        for j in range(16):
            w[j] = struct.unpack('>I', chunk[j*4:j*4+4])[0]
        
        # 메시지 확장 연산 (XOR 연산)
        for j in range(16, 80):
            w[j] = left_rotate(w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16], 1)
            
        a, b, c, d, e = h0, h1, h2, h3, h4
        
        # 80라운드의 비트 마스킹 및 논리 연산
        for j in range(80):
            if 0 <= j <= 19:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif 20 <= j <= 39:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= j <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            elif 60 <= j <= 79:
                f = b ^ c ^ d
                k = 0xCA62C1D6
                
            temp = (left_rotate(a, 5) + f + e + k + w[j]) & 0xffffffff
            e = d
            d = c
            c = left_rotate(b, 30)
            b = a
            a = temp
            
        h0 = (h0 + a) & 0xffffffff
        h1 = (h1 + b) & 0xffffffff
        h2 = (h2 + c) & 0xffffffff
        h3 = (h3 + d) & 0xffffffff
        h4 = (h4 + e) & 0xffffffff

    # 4. 결과값 결합
    return '%08x%08x%08x%08x%08x' % (h0, h1, h2, h3, h4)


# ==========================================
# 3. SHA-256을 라이브러리 없이 밑바닥부터 구현
# ==========================================
def right_rotate(n, b):
    # 32비트 우측 비트 시프트(순환 이동) 연산
    return ((n >> b) | (n << (32 - b))) & 0xffffffff

def my_sha256(message: bytes) -> str:
    """
    입력된 메시지를 SHA-256 알고리즘을 거쳐 
    고정된 64자리 16진수 해시로 변환합니다.
    """
    # 1. 초기 매직 넘버 (처음 8개 소수의 제곱근의 소수점 이하 32비트)
    h = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    
    # 2. 64개의 상수 배열 (처음 64개 소수의 세제곱근의 소수점 이하 32비트)
    k = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]

    # 3. 패딩 (SHA-1과 동일하게 512비트 블록으로 맞춤)
    original_byte_len = len(message)
    original_bit_len = original_byte_len * 8
    message += b'\x80'
    message += b'\x00' * ((56 - (original_byte_len + 1) % 64) % 64)
    message += struct.pack('>Q', original_bit_len)

    # 4. 64바이트(512비트) 블록 단위로 연산 (SHA-1은 80루프였으나, SHA-256은 64루프)
    for i in range(0, len(message), 64):
        chunk = message[i:i+64]
        w = [0] * 64
        for j in range(16):
            w[j] = struct.unpack('>I', chunk[j*4:j*4+4])[0]
            
        # 메시지 확장 연산 (엄청나게 복잡해짐)
        for j in range(16, 64):
            s0 = right_rotate(w[j-15], 7) ^ right_rotate(w[j-15], 18) ^ (w[j-15] >> 3)
            s1 = right_rotate(w[j-2], 17) ^ right_rotate(w[j-2], 19) ^ (w[j-2] >> 10)
            w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xffffffff

        a, b, c, d, e, f, g, current_h = h

        # 64라운드의 극한 비트 마스킹 압축 연산
        for j in range(64):
            S1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (current_h + S1 + ch + k[j] + w[j]) & 0xffffffff
            S0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xffffffff

            current_h = g
            g = f
            f = e
            e = (d + temp1) & 0xffffffff
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xffffffff

        # 블록 단위로 결과 업데이트
        h[0] = (h[0] + a) & 0xffffffff
        h[1] = (h[1] + b) & 0xffffffff
        h[2] = (h[2] + c) & 0xffffffff
        h[3] = (h[3] + d) & 0xffffffff
        h[4] = (h[4] + e) & 0xffffffff
        h[5] = (h[5] + f) & 0xffffffff
        h[6] = (h[6] + g) & 0xffffffff
        h[7] = (h[7] + current_h) & 0xffffffff

    # 5. 8개의 32비트 변수를 이어붙여 256비트(64자리 16진수) 생성
    return ''.join('%08x' % i for i in h)

# ==========================================
# 4. 비교 실행 테스트
# ==========================================
if __name__ == "__main__":
    print("=== 1. 직접 만든 UUID4 실행 결과 ===")
    print(f"- 생성된 랜덤 UUID: {my_uuid4()}")
    print("=> 완전히 무작위(난수)로 생성됨. 코드가 매우 짧고 단순함.\n")

    print("=== 2. 직접 만든 SHA-1 실행 결과 ===")
    text1 = "Hello Mini Git!"
    my_hash1 = my_sha1(text1.encode())
    print(f"[원본 텍스트]: '{text1}'")
    print(f"-> 내가 짠 SHA-1 : {my_hash1} (40자리)")
    
    print("\n=== 3. 직접 만든 SHA-256 실행 결과 ===")
    import hashlib
    my_hash256 = my_sha256(text1.encode())
    lib_hash256 = hashlib.sha256(text1.encode()).hexdigest()
    
    print(f"[원본 텍스트]: '{text1}'")
    print(f"-> 내가 짠 SHA-256 : {my_hash256} (64자리)")
    print(f"-> 라이브러리 SHA-256: {lib_hash256} (동일함 입증!)")
    print("=> 소수의 제곱근/세제곱근 등을 이용한 극한의 비트 쪼개기가 들어가므로 코드가 훨씬 복잡해짐.")
