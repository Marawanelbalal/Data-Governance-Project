import os
import pandas as pd
from ydata_profiling import ProfileReport

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        print("Warning: data/ directory does not exist. Run scripts\\load_data.py first.")
        exit(0)

    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv") and f != "nyc_restaurant_inspections_CLEAN.csv"]

    if not csv_files:
        print("Warning: No raw data found in data/. Profile skipped.")
        exit(0)

    raw_csv = csv_files[0]
    raw_path = os.path.join(DATA_DIR, raw_csv)

    print(f"Profiling raw data: {raw_path}")
    df = pd.read_csv(raw_path, low_memory=False)

    profile = ProfileReport(df, title="DOHMH Restaurant Inspections Data Profile", explorative=True)
    profile.to_file(os.path.join(DATA_DIR, "dohmh_restaurant_profile_report.html"))
    print("Data profiling report generated and saved as 'dohmh_restaurant_profile_report.html'")