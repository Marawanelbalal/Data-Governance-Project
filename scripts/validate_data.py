import os
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)


def validate_raw(df):
    required_cols = ["CAMIS", "BORO", "ZIPCODE", "GRADE", "SCORE", "INSPECTION DATE"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"Warning: Raw data missing columns: {missing}")
        return False
    print("Raw data validation: passed (required columns present)")
    return True


def validate_cleaned(df):
    for col in ["INSPECTION DATE", "GRADE DATE"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    valid_boros = ["MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN ISLAND"]
    valid_grades = ["A", "B", "C", "Z", "P", "N", "Not Yet Graded"]
    valid_flags = ["Critical", "Not Critical", "Not Applicable"]

    schema = DataFrameSchema(
        {
            "CAMIS": Column(pa.String, checks=Check.str_matches(r"^\d+$"), nullable=False),
            "BORO": Column(pa.String, checks=Check.isin(valid_boros), nullable=True),
            "ZIPCODE": Column(pa.String, checks=Check.str_matches(r"^\d{5}$"), nullable=True),
            "PHONE": Column(pa.String, checks=Check.str_matches(r"^\d{10}$"), nullable=True),
            "INSPECTION DATE": Column(pa.DateTime, checks=[Check(lambda s: s != pd.Timestamp("1900-01-01")), Check(lambda s: s <= pd.Timestamp.today())], nullable=False),
            "SCORE": Column(pa.Float, checks=Check.ge(0), nullable=True),
            "GRADE": Column(pa.String, checks=Check.isin(valid_grades), nullable=True),
            "CRITICAL FLAG": Column(pa.String, checks=Check.isin(valid_flags), nullable=True),
        },
        coerce=True
    )

    @pa.check("VIOLATION CODE", "VIOLATION DESCRIPTION")
    def violation_consistency(code, desc):
        return code.isna() == desc.isna()

    @pa.check("HAS_GRADE", "GRADE")
    def grade_flag_consistency(flag, grade):
        return flag == grade.notna()

    @pa.dataframe_check
    def no_duplicates(df):
        return ~df.duplicated()

    try:
        validated_df = schema.validate(df, lazy=True)
        print("Cleaned data validation: passed (all schema checks passed)")
        return True
    except pa.errors.SchemaErrors as e:
        print("Cleaned data validation: failed!")
        print(e.failure_cases)
        return False


if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        print("Warning: data/ directory does not exist. Validation skipped.")
        exit(0)

    raw_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv") and f != "nyc_restaurant_inspections_CLEAN.csv"]
    raw_path = os.path.join(DATA_DIR, raw_files[0]) if raw_files else None
    clean_path = os.path.join(DATA_DIR, "nyc_restaurant_inspections_CLEAN.csv")

    has_raw = raw_path and os.path.exists(raw_path)
    has_cleaned = os.path.exists(clean_path)

    if not has_raw and not has_cleaned:
        print("Warning: Neither raw nor cleaned data found in data/. Validation skipped.")
        exit(0)

    if has_raw:
        print(f"Validating raw data: {raw_path}")
        df_raw = pd.read_csv(raw_path, dtype={"PHONE": "string"}, encoding="latin-1", low_memory=False)
        validate_raw(df_raw)
    else:
        print("Warning: No raw data found in data/. Raw validation skipped.")

    if has_cleaned:
        print(f"Validating cleaned data: {clean_path}")
        df_clean = pd.read_csv(clean_path, dtype={"PHONE": "string"}, encoding="utf-8", low_memory=False)
        validate_cleaned(df_clean)
    else:
        print("Warning: No cleaned data found in data/. Cleaned validation skipped.")

    print("Validation complete.")