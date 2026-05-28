import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw/complaints_sample.csv")
PROCESSED_PATH = Path("data/processed/cleaned_complaints.csv")


def clean_column_name(col: str) -> str:
    return (
        col.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("?", "")
    )


def load_and_clean_complaints() -> pd.DataFrame:
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {RAW_PATH}. Add complaints_sample.csv to data/raw first."
        )

    df = pd.read_csv(RAW_PATH)
    df.columns = [clean_column_name(col) for col in df.columns]

    rename_map = {
        "complaint_id": "complaint_id",
        "product": "product",
        "sub_product": "sub_product",
        "issue": "issue",
        "sub_issue": "sub_issue",
        "consumer_complaint_narrative": "narrative",
        "company": "company",
        "state": "state",
        "company_response_to_consumer": "company_response",
        "timely_response": "timely_response",
        "date_received": "date_received",
    }

    available_cols = {}
    for old_col, new_col in rename_map.items():
        if old_col in df.columns:
            available_cols[old_col] = new_col

    df = df.rename(columns=available_cols)

    required_cols = [
        "complaint_id",
        "product",
        "issue",
        "narrative",
        "company",
        "company_response",
        "timely_response",
        "date_received",
    ]

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found columns: {list(df.columns)}")

    keep_cols = [
        "complaint_id",
        "product",
        "sub_product",
        "issue",
        "sub_issue",
        "narrative",
        "company",
        "state",
        "company_response",
        "timely_response",
        "date_received",
    ]

    keep_cols = [col for col in keep_cols if col in df.columns]
    df = df[keep_cols].copy()

    df = df.dropna(subset=["narrative"])
    df["narrative"] = df["narrative"].astype(str).str.strip()
    df = df[df["narrative"].str.len() > 50]

    MAX_ROWS = 5000
    if len(df) > MAX_ROWS:
        df = df.sample(n=MAX_ROWS, random_state=42)


    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)

    return df


if __name__ == "__main__":
    cleaned = load_and_clean_complaints()
    print(f"Saved {len(cleaned)} cleaned complaints to {PROCESSED_PATH}")
    print(cleaned.head())