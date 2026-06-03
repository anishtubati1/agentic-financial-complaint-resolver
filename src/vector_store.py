import pandas as pd
import chromadb
from pathlib import Path
from tqdm import tqdm

from src.embeddings import get_embedding

DATA_PATH = Path("data/processed/cleaned_complaints.csv")
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "cfpb_complaints"


def get_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection


def build_vector_store(limit: int = 500):
    """
    Builds a local Chroma vector store from cleaned CFPB complaints.
    Starts with a limit to control cost and speed.
    """
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {DATA_PATH}. Run src/data_loader.py first."
        )

    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["narrative"])
    df = df.head(limit)

    collection = get_chroma_collection()

    print(f"Building vector store with {len(df)} complaints...")

    for _, row in tqdm(df.iterrows(), total=len(df)):
        complaint_id = str(row["complaint_id"])
        narrative = str(row["narrative"])

        document_text = f"""
        Product: {row.get("product", "")}
        Issue: {row.get("issue", "")}
        Company: {row.get("company", "")}
        Complaint: {narrative}
        """

        embedding = get_embedding(document_text)

        metadata = {
            "complaint_id": complaint_id,
            "product": str(row.get("product", "")),
            "issue": str(row.get("issue", "")),
            "company": str(row.get("company", "")),
            "company_response": str(row.get("company_response", "")),
            "timely_response": str(row.get("timely_response", "")),
            "date_received": str(row.get("date_received", "")),
        }

        collection.upsert(
            ids=[complaint_id],
            documents=[narrative],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    print("Vector store build complete.")


def query_similar_complaints(query_text: str, top_k: int = 5) -> list[dict]:
    """
    Finds complaints most similar to the query text.
    """
    collection = get_chroma_collection()
    query_embedding = get_embedding(query_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    similar_cases = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, metadata, distance in zip(documents, metadatas, distances):
        similar_cases.append(
            {
                "complaint_id": metadata.get("complaint_id"),
                "product": metadata.get("product"),
                "issue": metadata.get("issue"),
                "company": metadata.get("company"),
                "company_response": metadata.get("company_response"),
                "timely_response": metadata.get("timely_response"),
                "date_received": metadata.get("date_received"),
                "similarity_distance": distance,
                "narrative_preview": doc[:500],
            }
        )

    return similar_cases


if __name__ == "__main__":
    build_vector_store(limit=200)