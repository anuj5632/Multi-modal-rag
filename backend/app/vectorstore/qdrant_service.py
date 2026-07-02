import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue

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
        vectors_config = VectorParams(
            size = 384,
            distance = Distance.COSINE
        )
    )

    print("Collection created successfully")


def insert_chunks(chunks,embedder, document_id, document_name):
    points = []

    for index, chunk in enumerate(chunks):
        embedding = embedder.embed(
            chunk["text"]
        )

        points.append(
            PointStruct(
                id = str(uuid.uuid4()),
                vector = embedding,
                payload = {
                    "document_id": document_id,
                    "document_name": document_name,
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
    if hasattr(client, "search"):
        return client.search(
            collection_name = COLLECTION_NAME,
            query_vector = query_embedding,
            limit = top_k
        )

    query_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
    )
    return query_result.points


def delete_document_chunks(document_id):
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
    )
    
