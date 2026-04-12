from openai import OpenAI
import os

# Load API key safely
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


def generate_expected_answer(question):
    """
    Generates a model answer using GPT.
    Returns None if API fails (NO fake answers).
    """

    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set")
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict examiner. "
                        "Provide a clear, structured model answer. "
                        "For math problems, show steps and final answer."
                    )
                },
                {"role": "user", "content": question}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("GPT ERROR:", e)
        return None