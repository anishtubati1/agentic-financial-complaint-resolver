import json
import pandas as pd

from src.agents.intake_agent import run_intake_agent
from src.agents.classification_agent import run_classification_agent
from src.agents.retrieval_agent import run_retrieval_agent

DATA_PATH = "data/processed/cleaned_complaints.csv"


def main():
    df = pd.read_csv(DATA_PATH)

    if df.empty:
        raise ValueError("cleaned_complaints.csv is empty.")

    complaint = df.iloc[0]
    complaint_text = complaint["narrative"]

    # These are the actual CFPB labels.
    # We DO NOT pass these into the Classification Agent.
    # We only use them after prediction for comparison/evaluation.
    actual_labels = {
        "actual_product": complaint.get("product"),
        "actual_issue": complaint.get("issue"),
        "actual_sub_issue": complaint.get("sub_issue"),
    }

    # This metadata is allowed because it does not directly give away
    # the product or issue labels we want the model to predict.
    non_label_metadata = {
        "complaint_id": complaint.get("complaint_id"),
        "company": complaint.get("company"),
        "company_response": complaint.get("company_response"),
        "timely_response": complaint.get("timely_response"),
        "date_received": complaint.get("date_received"),
        "state": complaint.get("state"),
    }

    print("\n=== Raw Complaint ===")
    print(complaint_text[:1000])

    print("\n=== Non-Label Metadata Sent to Agent ===")
    print(json.dumps(non_label_metadata, indent=2, default=str))

    print("\n=== Actual CFPB Labels Hidden from Agent ===")
    print(json.dumps(actual_labels, indent=2, default=str))

    print("\n=== Running Intake Agent ===")
    intake_result = run_intake_agent(complaint_text)
    print(json.dumps(intake_result, indent=2, default=str))

    print("\n=== Running Classification Agent ===")
    classification_result = run_classification_agent(
        complaint_text=complaint_text,
        metadata={
            "non_label_metadata": non_label_metadata,
            "intake_result": intake_result,
        },
    )
    print(json.dumps(classification_result, indent=2, default=str))

    print("\n=== Running Retrieval Agent ===")
    retrieval_result = run_retrieval_agent(
        complaint_text=complaint_text,
        top_k=5,
    )
    print(json.dumps(retrieval_result, indent=2, default=str))

    print("\n=== Comparison Against CFPB Labels ===")
    comparison = {
        "predicted_product": classification_result.get("predicted_product"),
        "actual_product": actual_labels.get("actual_product"),
        "predicted_issue": classification_result.get("predicted_issue"),
        "actual_issue": actual_labels.get("actual_issue"),
        "retrieved_case_count": len(retrieval_result.get("similar_cases", [])),
        "top_retrieved_product": (
            retrieval_result.get("similar_cases", [{}])[0].get("product")
            if retrieval_result.get("similar_cases")
            else None
        ),
        "top_retrieved_issue": (
            retrieval_result.get("similar_cases", [{}])[0].get("issue")
            if retrieval_result.get("similar_cases")
            else None
        ),
    }
    print(json.dumps(comparison, indent=2, default=str))


if __name__ == "__main__":
    main()