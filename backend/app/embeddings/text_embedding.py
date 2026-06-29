from sentence_transformers import SentenceTransformer


class TextEmbedder:

    def __init__(self):
        self.model = None

    def load_model(self):

        if self.model is None:

            print("Loading BGE Small...")

            self.model = SentenceTransformer(
                "BAAI/bge-small-en-v1.5"
            )

            print("Model loaded!")

    def embed(self, text):

        self.load_model()

        return self.model.encode(
            text,
            normalize_embeddings=True
        ).tolist()


embedder = TextEmbedder()