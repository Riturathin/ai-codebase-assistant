from openai import OpenAI
import os


class AnswerGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_answer(self, question: str, retrieved_chunks: list):
        if not retrieved_chunks:
            return "No relevant code found in the repository."

        context = ""

        for chunk in retrieved_chunks:
            context += f"""
File: {chunk['file_path']} (lines {chunk['start_line']}–{chunk['end_line']})
{chunk['content']}
---
"""

        prompt = f"""
You are an internal codebase assistant.

Answer the user's question using ONLY the provided code context.
If the answer is not present in the context, say you cannot find it.
Always mention file paths in your answer.

User Question:
{question}

Code Context:
{context}
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a codebase analysis assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        return response.choices[0].message.content
