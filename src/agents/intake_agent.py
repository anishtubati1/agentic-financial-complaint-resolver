import json
from pathlib import Path
from openai import OpenAI

from src.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

PROMPT_PATH = Path("src/prompts/intake_prompt.md")


def load_prompt() -> str:
    return PROMPT_PATH.read_text()


def run_intake_agent(complaint_text: str) -> dict:
    """
    Runs the intake agent on one complaint narrative.
    Returns structured JSON with summary, key facts, customer problem,
    customer request, and missing information.
    """
    if not complaint_text or not complaint_text.strip():
        raise ValueError("complaint_text cannot be empty.")

    system_prompt = load_prompt()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Consumer complaint:\n\n{complaint_text}",
            },
        ],
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "error": "Model did not return valid JSON.",
            "raw_output": content,
        }


if __name__ == "__main__":
    sample_complaint = """
    I checked my credit report and found an account that I do not recognize.
    I contacted the credit reporting company several times, but the incorrect
    account is still showing on my report. This is hurting my credit score and
    I need it investigated and removed if it is not mine.
    """

    result = run_intake_agent(sample_complaint)
    print(json.dumps(result, indent=2))