import os
import csv
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rsa_core import generate_rsa_keys, rsa_encrypt, rsa_decrypt


def load_column_data(filepath: str, column_name: str, sample_size: int = 5) -> list[str]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    values = [row[column_name] for row in rows if row.get(column_name)]
    return random.sample(values, min(sample_size, len(values)))


def main():
    print("=" * 80)
    print("RSA ENCRYPTION AND DECRYPTION")
    print("=" * 80)

    modulus, public_exp, private_exp = generate_rsa_keys(512)

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    data_path = os.path.join(data_dir, "nyc_restaurant_inspections_CLEAN.csv")

    text_samples = load_column_data(data_path, "DBA", 5)
    if not text_samples:
        text_samples = ["PIZZA PALACE", "SUSHI WORLD", "TACO BELL"]

    numeric_samples = load_column_data(data_path, "PHONE", 5)
    if not numeric_samples:
        numeric_samples = ["2125551234", "7185559876", "9175554567"]

    print(f"\nPlain Text                | Encrypted Text                         | Decrypted Text")
    print("-" * 90)
    for p in text_samples:
        c = rsa_encrypt(p, public_exp, modulus, "text")
        d = rsa_decrypt(c, private_exp, modulus, "text")
        print(f"{p[:24]:<24} | {str(c)[:40]:<42} | {d[:24]:<24}")

    print("-" * 90)
    for p in numeric_samples:
        c = rsa_encrypt(p, public_exp, modulus, "numeric")
        d = rsa_decrypt(c, private_exp, modulus, "numeric")
        print(f"{p[:24]:<24} | {str(c)[:40]:<42} | {d[:24]:<24}")


if __name__ == "__main__":
    main()