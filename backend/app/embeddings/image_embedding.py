from sentence_transformers import SentenceTransformer
from PIL import Image

class ImageEmbedder:
    """
    CLIP-based embedder for images and text.

    Uses sentence-transformers' clip-ViT-B-32, which maps both images and
    text into the SAME 512-dim vector space. This lets us:
      - embed extracted PDF images at ingestion time
      - embed a user's natural-language question at query time
      - compare them directly with cosine similarity in Qdrant

    Kept separate from TextEmbedder (BGE) because BGE only understands text
    and produces 384-dim vectors, incompatible with image search.
    """

    def __init__(self):
        self.model = None

    def load_model(self):
        if self.model is None:
            print("Loading CLIP (clip-ViT-B-32)...")
            self.model = SentenceTransformer("clip-ViT-B-32")
            print("CLIP model loaded!")

    
    def embed_image(self,image_path: str):
        self.load_model()
        image = Image.open(image_path).convert("RGB")
        return self.model.encode(
            image,
            normalize_embeddings = True
        ).tolist()
    
    def embed_text(self,text:str):
        self.load_model()
        return self.model.encode(
            text,
            normalize_embeddings = True
        ).tolist()
    
image_embedder = ImageEmbedder()