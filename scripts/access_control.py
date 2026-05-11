import os
import pandas as pd
import numpy as np

PUBLIC_COLS = ["DBA", "BORO", "CUISINE DESCRIPTION","INSPECTION DATE", "SCORE", "GRADE"]

ANALYST_COLS = PUBLIC_COLS + ["INSPECTION TYPE", "VIOLATION CODE", "VIOLATION DESCRIPTION",
"CRITICAL FLAG", "ACTION", "GRADE DATE","BUILDING", "STREET"]

INSPECTOR_COLS = "__ALL__"

POLICIES = {
    "inspector": {
        "required_department": "health",
        "required_clearance":  "high",
        "permitted_columns":   INSPECTOR_COLS,
        "can_modify":          True,
    },
    "analyst": {
        "required_department": "research",
        "required_clearance": "medium",
        "permitted_columns": ANALYST_COLS,
        "can_modify":          False,
    },
    "public": {
        "required_department": None,
        "required_clearance":"low",
        "permitted_columns":PUBLIC_COLS,
        "can_modify":False,
    },
}

CLEARANCE_RANK = {"low": 1, "medium": 2, "high": 3}


def matches_policy(user, policy_name):
    policy = POLICIES[policy_name]
    dept_required = policy["required_department"]
    if dept_required is not None and user["department"] != dept_required:
        return False
    required_rank = CLEARANCE_RANK.get(policy["required_clearance"], 999)
    user_rank = CLEARANCE_RANK.get(user["clearance"], 0)
    if user_rank < required_rank:
        return False
    return True


def get_matched_policy(user):
    for policy_name in ["inspector", "analyst", "public"]:
        if matches_policy(user, policy_name):
            return policy_name
    return None


def get_view(user, df, intent="read"):
    policy_name = get_matched_policy(user)

    if policy_name is None:
        print(f"  ✗ DENIED  — {user['name']}: no matching policy")
        return None

    policy = POLICIES[policy_name]

    if intent == "modify" and not policy["can_modify"]:
        print(f"  ✗ DENIED  — {user['name']}: policy '{policy_name}' is read-only")
        return None

    permitted = policy["permitted_columns"]
    if permitted == "__ALL__":
        view = df.copy()
    else:
        valid_cols = [c for c in permitted if c in df.columns]
        view = df[valid_cols].copy()

    print(f"  ✓ GRANTED — {user['name']}: policy='{policy_name}' | "
          f"columns visible: {len(view.columns)} | intent: {intent}")
    return view


if __name__ == "__main__":

    DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    DATA_DIR  = os.path.abspath(DATA_DIR)
    CLEAN_CSV = os.path.join(DATA_DIR, "nyc_restaurant_inspections_CLEAN.csv")

    if not os.path.exists(CLEAN_CSV):
        print(f"Error: cleaned CSV not found at:\n  {CLEAN_CSV}")
        print("Run scripts/clean_data.py first to generate it.")
        exit(1)

    print(f"Loading data from: {CLEAN_CSV}")
    df = pd.read_csv(CLEAN_CSV, dtype={"PHONE": "string"}, encoding="utf-8", low_memory=False)

    for col in ["INSPECTION DATE", "GRADE DATE"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    print(f"Loaded {len(df):,} rows, {df.shape[1]} columns\n")

    sample = df.head(3)

    users = [
        {"name": "Alice",   "department": "health",   "clearance": "high"},
        {"name": "Bob",     "department": "research", "clearance": "medium"},
        {"name": "Charlie", "department": "other",    "clearance": "low"},
        {"name": "Eve",     "department": "unknown",  "clearance": "low"},
    ]

    print("=" * 60)
    print("ABAC — READ ACCESS TEST")
    print("=" * 60)

    for user in users:
        print(f"\nUser: {user['name']} "
              f"(dept={user['department']}, clearance={user['clearance']})")
        view = get_view(user, sample, intent="read")
        if view is not None:
            print(f"  Columns: {list(view.columns)}")
            print(view.to_string(index=False))

    print("\n" + "=" * 60)
    print("ABAC — MODIFY ACCESS TEST")
    print("=" * 60)

    for user in users:
        print(f"\nUser: {user['name']} attempts MODIFY")
        get_view(user, sample, intent="modify")