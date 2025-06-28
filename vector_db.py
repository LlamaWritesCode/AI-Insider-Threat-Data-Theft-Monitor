from langchain_community.embeddings import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
import os

from convertcs import read_txt_file_as_string


# =============================
# Config & Globals
# =============================

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "ibm-hack"
NAMESPACE = "ns1"
DIMENSION = 1536
PINECONE_REGION = "us-east-1"

pc = Pinecone(api_key=PINECONE_API_KEY)


# =============================
# Initialize Pinecone
# =============================

def initialize_pinecone():
    if not pc.has_index(INDEX_NAME):
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            spec=ServerlessSpec(cloud="aws", region=PINECONE_REGION),
            embed={
                "model": "llama-text-embed-v2",
                "field_map": {"text": "chunk_text"}
            }
        )
        print(f"✅ Created Pinecone index '{INDEX_NAME}'")
    else:
        print(f"✅ Pinecone index '{INDEX_NAME}' already exists.")

    index = pc.Index(host=f"https://{INDEX_NAME}-lgywj80.svc.aped-4627-b74a.pinecone.io")
    print(f"✅ Connected to Pinecone index '{INDEX_NAME}'")
    return index


# =============================
# Split Text into Chunks
# =============================

def split_into_chunks(text, max_words=100, overlap=30):
    if overlap >= max_words:
        raise ValueError("`overlap` must be smaller than `max_words`.")
    
    words = text.split()
    chunks = []
    step = max_words - overlap

    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)

    return chunks


# =============================
# Create Embeddings
# =============================

def create_embeddings(text_chunks):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectors = embeddings.embed_documents(text_chunks)
    print(f"✅ Created {len(vectors)} embeddings.")
    return vectors, embeddings


# =============================
# Upsert Chunks to Pinecone
# =============================

def upsert_chunks(index, chunks, vectors):
    records = []
    for i, chunk in enumerate(chunks):
        records.append({
            "_id": f"chunk-{i}",
            "embedding": vectors[i],
            "chunk_text": chunk,
            "category": "resume"
        })
    index.upsert(
        vectors=[
            (r["_id"], r["embedding"], {
                "chunk_text": r["chunk_text"],
                "category": r["category"]
            })
            for r in records
        ],
        namespace=NAMESPACE
    )
    print(f"✅ Upserted {len(records)} chunks to Pinecone.")


# =============================
# Search Index
# =============================

def search_index(index, embeddings, query_file):
    query_text = read_txt_file_as_string(query_file)
    query_vector = embeddings.embed_query(query_text)

    results = index.query(
        vector=query_vector,
        top_k=3,
        namespace=NAMESPACE,
        include_metadata=True
    )

    context_list = []
    if not results['matches']:
        print("⚠️ No results found.")
    else:
        for hit in results['matches']:
            chunk_id = hit['id']
            score = round(hit['score'], 4)
            chunk_text = hit['metadata']['chunk_text']

            context = (
                f"=== Match ===\n"
                f"ID: {chunk_id}\n"
                f"Similarity Score: {score}\n\n"
                f"{chunk_text}\n"
                f"====================\n"
            )
            context_list.append(context)
    return context_list


# =============================
# Main Pipeline
# =============================

if __name__ == "__main__":
    # 1. Initialize Pinecone
    index = initialize_pinecone()

    # 2. Load log file & split into chunks
    data = read_txt_file_as_string("anomalies.txt")
    chunks = split_into_chunks(data, max_words=50, overlap=30)

    # 3. Embed chunks & upsert
    vectors, embeddings = create_embeddings(chunks)
    upsert_chunks(index, chunks, vectors)

    # 4. Search index using another file
    contexts = search_index(index, embeddings, "normal_log.txt")

    # 5. Show results clearly
    print("\n==== SEARCH RESULTS ====\n")
    for context in contexts:
        print(context)
