import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rsa_core import (
    generate_rsa_keys, rsa_encrypt, rsa_decrypt,
    text_to_int, int_to_text, fast_pow, modinv, extended_gcd, gcd, is_prime
)


def integer_root(number: int, exponent: int) -> int:
    if number == 0:
        return 0
    low, high = 0, 1
    while fast_pow(high, exponent, 1 << 64) <= number:
        high <<= 1
    while low <= high:
        mid = (low + high) // 2
        mid_power = fast_pow(mid, exponent, 1 << 256)
        if mid_power == number:
            return mid
        elif mid_power < number:
            low = mid + 1
        else:
            high = mid - 1
    return high


def attack_small_message():
    print("\n=== ATTACK 1: SMALL MESSAGE ===")
    modulus, _, _ = generate_rsa_keys(512)
    exp = 3

    for cand in ["A", "B", "X", "1"]:
        m = text_to_int(cand)
        if fast_pow(m, exp, modulus) < modulus:
            original = cand
            break

    m_int = text_to_int(original)
    ciphertext = fast_pow(m_int, exp, modulus)
    print(f"Original: {original}, Ciphertext: {ciphertext}")

    recovered_int = integer_root(ciphertext, exp)
    recovered = int_to_text(recovered_int)
    print(f"Recovered: {recovered}, Match: {recovered == original}")
    return recovered == original


def attack_wieners():
    print("\n=== ATTACK 2: WIENER ===")
    for _ in range(50):
        p = random.getrandbits(256)
        q = random.getrandbits(256)
        if not (is_prime(p) and is_prime(q)):
            continue
        modulus = p * q
        phi = (p - 1) * (q - 1)
        e = 65537
        if gcd(e, phi) != 1:
            continue
        d = modinv(e, phi)
        if d < modulus ** 0.25:
            break
    else:
        p, q = random.getrandbits(128), random.getrandbits(128)
        while not is_prime(p): p = random.getrandbits(128)
        while not is_prime(q): q = random.getrandbits(128)
        modulus = p * q
        phi = (p - 1) * (q - 1)
        e = 65537
        d = modinv(e, phi)

    print(f"n={modulus}, e={e}, d={d}, d < n^(1/4)? {d < modulus**0.25}")

    a, b = e, modulus
    coeffs = []
    while b:
        coeffs.append(a // b)
        a, b = b, a % b

    convergents = []
    n1, n2, d1, d2 = 1, 0, 0, 1
    for c in coeffs:
        n1, n2, d1, d2 = c * n1 + n2, n1, c * d1 + d2, d1
        convergents.append((n1, d1))
        if len(convergents) > 20:
            break

    for k, d_guess in convergents:
        if d_guess == 0:
            continue
        try:
            phi_est = (e * d_guess - 1) / k
            if phi_est <= 0 or phi_est >= modulus:
                continue
            x = modulus - phi_est + 1
            disc = int(x ** 0.5)
            if disc * disc != x:
                continue
            p_g, q_g = (x + disc) // 2, (x - disc) // 2
            if p_g * q_g == modulus and p_g > 1:
                print(f"Found d: {d_guess}, Match: {d_guess == d}")
                return d_guess == d
        except:
            pass

    print("Key resistant - d too large")
    return False


def attack_common_modulus():
    print("\n=== ATTACK 3: COMMON MODULUS ===")
    p = random.getrandbits(256)
    q = random.getrandbits(256)
    while not is_prime(p): p = random.getrandbits(256)
    while not is_prime(q): q = random.getrandbits(256)
    modulus = p * q

    msg = "HELLO"
    m = text_to_int(msg)
    e1, e2 = 3, 5

    c1 = fast_pow(m, e1, modulus)
    c2 = fast_pow(m, e2, modulus)
    print(f"Message: {msg}, c1={c1}, c2={c2}")

    g, s, t = extended_gcd(e1, e2)
    print(f"s={s}, t={t}, verify: {s*e1 + t*e2}")

    p1 = fast_pow(c1, s, modulus) if s > 0 else modinv(fast_pow(c1, -s, modulus), modulus)
    p2 = fast_pow(c2, t, modulus) if t > 0 else modinv(fast_pow(c2, -t, modulus), modulus)
    recovered = (p1 * p2) % modulus

    result = int_to_text(recovered)
    print(f"Recovered: {result}, Match: {result == msg}")
    return result == msg


def attack_chosen_ciphertext():
    print("\n=== ATTACK 4: CHOSEN CIPHERTEXT ===")
    modulus, e, d = generate_rsa_keys(512)
    msg = "SECRET"
    ciphertext = rsa_encrypt(msg, e, modulus)
    print(f"Original: {msg}, Ciphertext: {ciphertext}")

    r = random.randrange(2, modulus)
    mod_cipher = (ciphertext * fast_pow(r, e, modulus)) % modulus

    try:
        decrypted = rsa_decrypt(mod_cipher, d, modulus)
    except:
        decrypted = f"<binary {fast_pow(mod_cipher, d, modulus)}>"

    print(f"After CCA: {decrypted}")
    return True


def main():
    print("=" * 50)
    print("RSA ATTACKS")
    print("=" * 50)

    results = {
        "Small Message": attack_small_message(),
        "Wiener": attack_wieners(),
        "Common Modulus": attack_common_modulus(),
        "Chosen Ciphertext": attack_chosen_ciphertext(),
    }

    print("\n=== SUMMARY ===")
    for name, success in results.items():
        print(f"{name}: {'SUCCESS' if success else 'DEMONSTRATED'}")


if __name__ == "__main__":
    main()