import os
import mimetypes

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
    
    def build_audio_context(self, retrieved_audio):
        context = ""

        for chunk in retrieved_audio:
            timestamp = chunk["timestamp"]
            name = chunk["document_name"]
            text = chunk["text"]

            context += f"[{name} @ {timestamp}]: {text}"
        
        return context

    def _image_part(self, image_path):
        """Load an image off disk and wrap it as a Gemini Part for vision input."""
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            mime_type = "image/png"

        with open(image_path, "rb") as f:
            data = f.read()

        return types.Part.from_bytes(data=data, mime_type=mime_type)

    def generate_answer(self, question, retrieved_chunks, retrieved_images=None, temperature=0.1):
        """
        Backwards-compatible entry point. If retrieved_images is provided and
        non-empty, this calls Gemini in vision mode so the model can
        actually look at the retrieved figures/diagrams/photos, not just
        text describing them. If retrieved_audio is provided, transcript
        excerpts with timestamps are folded into the context so answers
        can cite "at 04:12" the same way they cite "page 7".
        """

        if self.client is None:
            return "LLM is not configured. Install google-genai and set GEMINI_API_KEY to enable answer generation."

        retrieved_images = retrieved_images or []
        retrieved_audio = retrieved_audio or []

        context = self.build_context(retrieved_chunks)
        audio_context = self.build.audio_context(retrieved_audio)

        image_reference_list = "\n".join(
            f"- Image {i+1}: page {img['page']} (from {img['document_name']})"
            for i, img in enumerate(retrieved_images)
        )

        rules = """You are an enterprise document assistant.

Rules:

1. Answer ONLY using the provided text context, transcript excerpts, and (if given) attached images.
2. If the answer is not in any of the provided material, respond with "I don't know".
3. Mention page numbers for document context, and timestamps (mm:ss) for transcript excerpts, whenever possible.
4. Keep answers concise and factual.
5. If an attached image is relevant to the answer, explicitly reference it (e.g. "as shown in Image 2 on page 7").
"""

        sections = [rules]

        if context:
            sections.append(f"Document Context:\n\n{context}")

        if audio_context:
            sections.append(f"Transcript Excerpts:\n\n{audio_context}")

        if retrieved_images:
            sections.append(f"Attached Images (in order):\n{image_reference_list}")

        sections.append(f"Question:\n{question}\n\nAnswer:")

        prompt = "\n\n".join(sections)

        contents = [prompt]

        for img in retrieved_images:
            try:
                contents.append(self._image_part(img["image_path"]))
            except Exception as e:
                print(f"Could not attach image {img.get('image_path')}: {e}")

        response = self.client.models.generate_content(
            model=self.model,

            contents=contents,

            config=types.GenerateContentConfig(
                temperature=temperature
            )
        )

        return response.text


generator = RAGGenerator()

