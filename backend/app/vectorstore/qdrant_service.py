import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.core.config import settings

COLLECTION_NAME = "documents"
IMAGE_COLLECTION_NAME = "images"
AUDIO_COLLECTION_NAME = "audio_chunks"

TEXT_VECTOR_SIZE = 384   # BGE-small
IMAGE_VECTOR_SIZE = 512  # clip-ViT-B-32
# Audio transcript chunks are plain text, so they reuse the same BGE
# embedder as PDF chunks (no separate audio embedding model needed).
AUDIO_VECTOR_SIZE = 384  # BGE-small

client = QdrantClient(
    host = settings.qdrant_host,
    port = settings.qdrant_port
)


def _ensure_collection(name: str, vector_size: int):
    collections = client.get_collections()

    existing = [
        collection.name
        for collection in collections.collections
    ]

    if name in existing:
        print(f"Collection '{name}' already existed")
        return

    client.create_collection(
        collection_name = name,
        vectors_config = VectorParams(
            size = vector_size,
            distance = Distance.COSINE
        )
    )

    print(f"Collection '{name}' created successfully")


def create_collection():
    """Text chunk collection (BGE, 384-dim). Kept for backwards compatibility."""
    _ensure_collection(COLLECTION_NAME, TEXT_VECTOR_SIZE)


def create_image_collection():
    """Image collection (CLIP, 512-dim)."""
    _ensure_collection(IMAGE_COLLECTION_NAME, IMAGE_VECTOR_SIZE)


def create_audio_collection():
    """Audio transcript chunk collection (BGE, 384-dim)."""
    _ensure_collection(AUDIO_COLLECTION_NAME, AUDIO_VECTOR_SIZE)


def insert_chunks(chunks, embedder, document_id, document_name):
    points = []
    inserted = []

    for index, chunk in enumerate(chunks):
        embedding = embedder.embed(
            chunk["text"]
        )

        point_id = str(uuid.uuid4())

        points.append(
            PointStruct(
                id = point_id,
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

        inserted.append({
            "id": point_id,
            "document_id": document_id,
            "document_name": document_name,
            "page": chunk["page"],
            "text": chunk["text"],
        })

    client.upsert(
        collection_name = COLLECTION_NAME,
        points = points
    )

    print(
        f"{len(points)} chunks inserted successfully"
    )

    return inserted


def insert_images(images, image_embedder, document_id, document_name):
    """
    images: list of {"page": int, "image_path": str} from image_extractor.extract_images
    image_embedder: an ImageEmbedder instance
    """
    if not images:
        return

    points = []

    for image in images:
        try:
            embedding = image_embedder.embed_image(image["image_path"])
        except Exception as e:
            # A corrupt / unreadable extracted image shouldn't kill the whole upload
            print(f"Skipping image {image['image_path']}: {e}")
            continue

        points.append(
            PointStruct(
                id = str(uuid.uuid4()),
                vector = embedding,
                payload = {
                    "document_id": document_id,
                    "document_name": document_name,
                    "page": image["page"],
                    "image_path": image["image_path"],
                }
            )
        )

    if not points:
        return

    client.upsert(
        collection_name = IMAGE_COLLECTION_NAME,
        points = points
    )

    print(
        f"{len(points)} images inserted successfully"
    )


def insert_audio_chunks(chunks, embedder, document_id, document_name, file_path=None):
    """
    chunks: list of {"start": float, "end": float, "chunk_index": int, "text": str}
    embedder: TextEmbedder instance (BGE) - transcripts are plain text
    file_path: path to the saved audio file, stored in the payload so the
    API layer can build a playable URL back to the original recording.
    """
    if not chunks:
        return

    points = []

    for chunk in chunks:
        embedding = embedder.embed(chunk["text"])

        points.append(
            PointStruct(
                id = str(uuid.uuid4()),
                vector = embedding,
                payload = {
                    "document_id": document_id,
                    "document_name": document_name,
                    "start": chunk["start"],
                    "end": chunk["end"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "file_path": file_path,
                }
            )
        )

    client.upsert(
        collection_name = AUDIO_COLLECTION_NAME,
        points = points
    )

    print(
        f"{len(points)} audio chunks inserted successfully"
    )


def search_chunks(query_embedding, top_k = 5):
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


def search_images(query_embedding, top_k = 3):
    if hasattr(client, "search"):
        return client.search(
            collection_name = IMAGE_COLLECTION_NAME,
            query_vector = query_embedding,
            limit = top_k
        )

    query_result = client.query_points(
        collection_name=IMAGE_COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
    )
    return query_result.points


def search_audio_chunks(query_embedding, top_k = 5):
    if hasattr(client, "search"):
        return client.search(
            collection_name = AUDIO_COLLECTION_NAME,
            query_vector = query_embedding,
            limit = top_k
        )

    query_result = client.query_points(
        collection_name=AUDIO_COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
    )
    return query_result.points


def scroll_all_chunks(batch_size=256):
    """
    Yields every point currently stored in the text collection. Used to
    backfill the BM25 index from chunks that were embedded/inserted
    before hybrid search existed (v1-v3 uploads).
    """
    offset = None

    while True:
        points, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=batch_size,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        for point in points:
            yield {
                "id": str(point.id),
                "document_id": point.payload.get("document_id", "unknown"),
                "document_name": point.payload.get("document_name", "Document"),
                "page": point.payload.get("page"),
                "text": point.payload.get("text", ""),
            }

        if offset is None:
            break


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


def delete_document_images(document_id):
    try:
        client.delete(
            collection_name=IMAGE_COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
        )
    except Exception as e:
        # Collection may not exist yet if no images have ever been indexed
        print(f"delete_document_images skipped: {e}")


def delete_document_audio(document_id):
    try:
        client.delete(
            collection_name=AUDIO_COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
        )
    except Exception as e:
        # Collection may not exist yet if no audio has ever been indexed
        print(f"delete_document_audio skipped: {e}")
