import kagglehub
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)

if __name__ == "__main__":
    path = kagglehub.dataset_download("new-york-city/nyc-inspections")

    csv_file = next(f for f in os.listdir(path) if f.endswith(".csv"))

    src = os.path.join(path, csv_file)
    dst = os.path.join(DATA_DIR, csv_file)
    os.makedirs(DATA_DIR, exist_ok=True)

    df = pd.read_csv(src, dtype={"PHONE": "string"}, encoding="latin-1", low_memory=False)

    df.to_csv(dst, index=False)
    print(f"Saved raw data to {dst} ({df.shape[0]:,} rows, {df.shape[1]} columns)")