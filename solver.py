from openai import OpenAI
import os
import json
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_json(text):
    """Extract JSON even if GPT adds extra text"""
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        return None


def solve_question(question):

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a mathematics solver for lower secondary curriculum.

IMPORTANT RULES:
- Solve all word problems step by step internally
- Output ONLY valid JSON
- No explanation, no markdown, no text outside JSON

FORMAT RULES:

If multi-part question:
{
  "a": value,
  "b": value,
  "c": value
}

If single answer:
{
  "answer": value
}
"""
                },
                {"role": "user", "content": question}
            ]
        )

        content = response.choices[0].message.content

        result = extract_json(content)

        if result:
            return result

        return None

    except Exception as e:
        print("Solver error:", e)
        return None