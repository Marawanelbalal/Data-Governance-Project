import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)

if __name__ == "__main__":
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv") and f != "nyc_restaurant_inspections_CLEAN.csv"]

    if not csv_files:
        print(r"Error: No raw data found in data/. Run scripts\load_data.py first.")
        exit(1)

    raw_csv = csv_files[0]
    raw_path = os.path.join(DATA_DIR, raw_csv)

    df = pd.read_csv(raw_path, dtype={"PHONE": "string"}, encoding="latin-1", low_memory=False)

    df["CUISINE DESCRIPTION"] = df["CUISINE DESCRIPTION"].str.replace(
        r"Caf[^\s/]+", "Cafe", regex=True
    )

    for col in ["INSPECTION DATE", "GRADE DATE", "RECORD DATE"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    df["ZIPCODE"] = df["ZIPCODE"].apply(lambda x: str(int(x)).zfill(5) if pd.notna(x) else np.nan)

    df["CAMIS"] = df["CAMIS"].astype(str)

    df = df.drop_duplicates(keep="first")

    df["BORO"] = df["BORO"].replace("Missing", np.nan)

    sentinel_mask = df["INSPECTION DATE"] == pd.Timestamp("1900-01-01")
    df["IS_SENTINEL_DATE"] = sentinel_mask
    df.loc[sentinel_mask, "INSPECTION DATE"] = pd.NaT

    neg_mask = df["SCORE"] < 0
    df["SCORE_INVALID"] = neg_mask
    df.loc[neg_mask, "SCORE"] = np.nan

    df["SCORE_EXTREME"] = df["SCORE"] > 100

    df["HAS_GRADE"] = df["GRADE"].notna()

    df["PHONE"] = df["PHONE"].astype("string").str.replace(r"\.0$", "", regex=True).str.replace(r"\D", "", regex=True)
    df["PHONE"] = df["PHONE"].where(df["PHONE"].str.len() == 10, None)

    df["VIOLATION_MISMATCH"] = df["VIOLATION CODE"].isna() ^ df["VIOLATION DESCRIPTION"].isna()

    df = df.drop(columns=["RECORD DATE"])

    df = df[df["IS_SENTINEL_DATE"] == False]
    df = df[df["VIOLATION_MISMATCH"] == False]

    clean_path = os.path.join(DATA_DIR, "nyc_restaurant_inspections_CLEAN.csv")
    df.to_csv(clean_path, index=False, encoding="utf-8")
    print(f"Saved cleaned data to {clean_path} ({df.shape[0]:,} rows, {df.shape[1]} columns)")