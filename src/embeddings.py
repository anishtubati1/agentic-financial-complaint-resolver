from openai import OpenAI

from src.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str) -> list[float]:
    """
    Creates an embedding vector for a piece of text.
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )

    return response.data[0].embedding