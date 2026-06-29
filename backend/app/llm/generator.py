from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class RAGGenerator:

    def __init__(self):

        api_key = os.getnev("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        self.client = genai.Client(
            api_key = api_key
        )

        self.model = "gemini-2.5-flash"

    def build_context(self,retrieved_chunk):
        context = ""

        for chunk in retrieved_chunks:

            page = chunk["page"]
            text = chunk["text"]

            context += f"Page {page}: {text}\n"
            context += text
            context += "\n\n"

        return context
    
    def generate_answer(self,question,retrieved_chunks):

        context = self.build_context(retrieved_chunks)

        prompt = f"""

You are an enterprise document assistant.repr

Rules:

1. Answer ONLY using the provided context.
2. If the answer is not in the context, respond with "I don't know".
3. Mention page numbers whenever possible.
4. Keep answers concise and factual.repr

Context:

{context}

{question}

Answer:
"""

        response = self.client.models.generate_content(
            model=self.model,

            contents=prompt,

            config=types.GenerateContentConfig(
                temperature=0.1
            )
        )

        return response.text


generator = RAGGenerator()