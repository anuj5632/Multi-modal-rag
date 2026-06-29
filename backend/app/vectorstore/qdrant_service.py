from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct

COLLECTION_NAME = "documents"

client = QdrantClient(
    host = "localhost",
    port = 6333
)

def create_collection():
    collections = client.get_collections()

    existing = [
        collection.name
        for collection in collections.collections
    ]

    if COLLECTION_NAME in existing:
        print("Collection already existed")
        return 
    
    client.create_collection(
        collection_name = COLLECTION_NAME,
        vectors_config = {
            "embedding" : VectorParams(
                size = 384,
                distance = Distance.COSINE
            )
        }
    )

    print("Collection created successfully")


def insert_chunks(chunks,embedder):
    points = []

    for index, chunk in enumerate(chunks):
        embedding = embedder.embed(
            chunk["text"]
        )

        points.append(
            PointStruct(
                id = index,
                vector = embedding,
                payload = {
                    "page" : chunk["page"],

                    "chunk_index":
                    chunk["chunk_index"],

                    "text" : chunk["text"]
                }
            )
        )
    
    client.upsert(
        collection_name = COLLECTION_NAME,
        points = points
    )

    print(
        f"{len(points)} chunks inserted successfully"
    )


def search_chunks(query_embedding,top_k = 5):
    results = client.search(
        collection_name = COLLECTION_NAME,

        query_vector = query_embedding,

        limit = top_k
    )

    return results
    
