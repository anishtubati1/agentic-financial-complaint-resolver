import json
import pandas as pd

from src.agents.intake_agent import run_intake_agent
from src.agents.classification_agent import run_classification_agent

DATA_PATH = "data/processed/cleaned_complaints.csv"


def main():
    df = pd.read_csv(DATA_PATH)

    if df.empty:
        raise ValueError("cleaned_complaints.csv is empty.")

    complaint = df.iloc[0]
    complaint_text = complaint["narrative"]

    metadata = {
        "complaint_id": complaint.get("complaint_id"),
        "product": complaint.get("product"),
        "issue": complaint.get("issue"),
        "company": complaint.get("company"),
        "company_response": complaint.get("company_response"),
        "timely_response": complaint.get("timely_response"),
        "date_received": complaint.get("date_received"),
    }

    print("\n=== Raw Complaint ===")
    print(complaint_text[:1000])

    print("\n=== CFPB Metadata ===")
    print(json.dumps(metadata, indent=2, default=str))

    print("\n=== Running Intake Agent ===")
    intake_result = run_intake_agent(complaint_text)
    print(json.dumps(intake_result, indent=2))

    print("\n=== Running Classification Agent ===")
    classification_result = run_classification_agent(
        complaint_text=complaint_text,
        metadata={
            "cfpb_metadata": metadata,
            "intake_result": intake_result,
        },
    )
    print(json.dumps(classification_result, indent=2))


if __name__ == "__main__":
    main()