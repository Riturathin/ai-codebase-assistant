import os

from openai import OpenAI


class AnswerGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=api_key)

    def stream_answer(self, question: str, retrieved_chunks: list):
        """
        Streams a grounded answer based only on retrieved code chunks.
        """

        if not retrieved_chunks:
            yield "No relevant code found in the repository."
            return

        context_blocks = []

        for chunk in retrieved_chunks:
            context_blocks.append(
                f"""
    File: {chunk['file_path']} (lines {chunk['start_line']}–{chunk['end_line']})
    {chunk['content']}
    ---
    """
            )

        context = "\n".join(context_blocks)

        prompt = f"""
            You are an internal codebase assistant.

            RULES:
            - Use ONLY the provided code context.
            - You may analyze structure, complexity, repetition, and patterns.
            - Do NOT invent files that are not shown.
            - If the context is insufficient, say so.
            - Mention file paths and line numbers when relevant.
            - Be concise and technical.

            User Question:
            {question}

            Code Context:
            {context}
        """

        with self.client.responses.stream(
            model="gpt-4o-mini",
            input=prompt,
            temperature=0,
        ) as stream:

            full_text = ""

            for event in stream:
                if event.type == "response.output_text.delta":
                    delta = event.delta or ""

                    # Prevent duplication by only yielding new text
                    if not full_text.endswith(delta):
                        yield delta
                        full_text += delta
