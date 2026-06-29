from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200,
)

def create_chunks(pages):
    chunks = []

    for page_data in pages:
        page_number = page_data["page"]

        text = page_data["text"]

        text_chunks = splitter.split_text(text)

        for index, chunk in enumerate(text_chunks):
            chunks.append(
                {
                    "page" : page_number,
                    "chunk_index" : index + 1,
                    "chunk_text" : chunk
                }
            )

    return chunks

