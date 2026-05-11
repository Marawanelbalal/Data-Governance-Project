import random


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y


def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m


def fast_pow(base, exp, mod):
    if mod == 1:
        return 0
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result


def is_prime(n, k=40):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = fast_pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = fast_pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def generate_prime(bits):
    while True:
        p = random.getrandbits(bits)
        p |= (1 << (bits - 1)) | 1
        if is_prime(p):
            return p


def generate_rsa_keys(bits=512):
    p = generate_prime(bits)
    q = generate_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    while gcd(e, phi) != 1:
        e = random.randrange(3, phi, 2)
    d = modinv(e, phi)
    return n, e, d


def text_to_int(text):
    return int.from_bytes(text.encode('utf-8'), 'big')


def int_to_text(num):
    if num == 0:
        return ""
    byte_length = (num.bit_length() + 7) // 8
    return num.to_bytes(byte_length, 'big').decode('utf-8')


def rsa_encrypt(plaintext: str, exponent: int, modulus: int, data_type: str = "text") -> int:
    if data_type == "numeric":
        message_int = int(plaintext)
    else:
        message_int = text_to_int(plaintext)
    return fast_pow(message_int, exponent, modulus)


def rsa_decrypt(ciphertext: int, private_exponent: int, modulus: int, data_type: str = "text") -> str:
    decrypted_int = fast_pow(ciphertext, private_exponent, modulus)
    if data_type == "numeric":
        return str(decrypted_int)
    return int_to_text(decrypted_int)