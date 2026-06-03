import json
import time

from src.vector_store import query_similar_complaints


def run_retrieval_agent(complaint_text: str, top_k: int = 5) -> dict:
    """
    Retrieves similar CFPB complaints from the vector store.
    """
    if not complaint_text or not complaint_text.strip():
        raise ValueError("complaint_text cannot be empty.")

    print("Running retrieval agent...")
    start = time.time()

    similar_cases = query_similar_complaints(
        query_text=complaint_text,
        top_k=top_k,
    )

    elapsed_time = time.time() - start
    print(f"Retrieval agent took {elapsed_time:.2f} seconds")

    return {
        "similar_cases": similar_cases
    }


if __name__ == "__main__":
    sample_complaint = """
    I saw a credit card offer that said I had outstanding approval odds.
    After applying, I was approved for a line of credit instead of the credit card
    I thought I was applying for. I believe the offer was misleading.
    """

    result = run_retrieval_agent(sample_complaint)
    print(json.dumps(result, indent=2, default=str))