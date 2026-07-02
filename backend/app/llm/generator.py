import os

from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

load_dotenv()

class RAGGenerator:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        self.client = None
        if api_key and genai is not None:
            self.client = genai.Client(
                api_key = api_key
            )

        self.model = "gemini-2.5-flash"

    def build_context(self,retrieved_chunk):
        context = ""

        for chunk in retrieved_chunk:

            page = chunk["page"]
            text = chunk["text"]

            context += f"Page {page}: {text}\n"
            context += "\n"

        return context
    
    def generate_answer(self,question,retrieved_chunks, temperature=0.1):

        if self.client is None:
            return "LLM is not configured. Install google-genai and set GEMINI_API_KEY to enable answer generation."

        context = self.build_context(retrieved_chunks)

        prompt = f"""

You are an enterprise document assistant.

Rules:

1. Answer ONLY using the provided context.
2. If the answer is not in the context, respond with "I don't know".
3. Mention page numbers whenever possible.
4. Keep answers concise and factual.

Context:

{context}

Question:
{question}

Answer:
"""

        response = self.client.models.generate_content(
            model=self.model,

            contents=prompt,

            config=types.GenerateContentConfig(
                temperature=temperature
            )
        )

        return response.text


generator = RAGGenerator()