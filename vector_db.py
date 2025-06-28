import os
from langchain_community.embeddings import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

from convertcs import read_txt_file_as_string

# =============================
# Config & Global Vars
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
            spec=ServerlessSpec(cloud="aws", region=PINECONE_REGION)
        )
        print(f"✅ Created Pinecone index '{INDEX_NAME}'")
    else:
        print(f"✅ Pinecone index '{INDEX_NAME}' already exists.")

    index = pc.Index(host=f"https://{INDEX_NAME}-lgywj80.svc.aped-4627-b74a.pinecone.io")
    print(f"✅ Connected to Pinecone index '{INDEX_NAME}'")
    return index


# =============================
# Signal extraction from log lines
# =============================

def extract_signal(log_line: str) -> str:
    """
    Extract the signal parts of a log line:
    Keep only suspicious indicators.
    """
    parts = log_line.strip().split(',')
    if len(parts) < 7:
        return ""

    event_id = parts[4].strip()
    task_category = parts[5].strip()
    message = parts[6].strip().lower()

    suspicious_keywords = [
        "suspicious", "failed", "lockout", "audit log cleared", "suspicious connection"
    ]

    # If message contains any suspicious word, keep it
    if any(kw in message for kw in suspicious_keywords):
        return f"EventID:{event_id} Category:{task_category} Message:{message}"

    return ""


# =============================
# Chunking signal text
# =============================

def split_into_chunks(text, max_words=50, overlap=20):
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
# Embedding
# =============================

def create_embeddings(text_chunks):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectors = embeddings.embed_documents(text_chunks)
    print(f"✅ Created {len(vectors)} embeddings.")
    return vectors, embeddings


# =============================
# Upsert
# =============================

def upsert_chunks(index, chunks, vectors):
    records = []
    for i, chunk in enumerate(chunks):
        records.append({
            "_id": f"chunk-{i}",
            "embedding": vectors[i],
            "chunk_text": chunk,
            "category": "log_signal"
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
# Search
# =============================

def search_index(index, embeddings, query_file):
    query_text = read_txt_file_as_string(query_file)

    # Extract signal from query file too!
    signal_lines = [
        extract_signal(line) for line in query_text.split('\n')
    ]
    signal_lines = [line for line in signal_lines if line.strip()]
    signal_text = " ".join(signal_lines)

    if not signal_text:
        print("⚠️ Query file did not contain suspicious signals.")
        return []

    query_vector = embeddings.embed_query(signal_text)

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
            context_list.append(
                f"Chunk {hit['id']} (score: {hit['score']}): "
                f"{hit['metadata']['chunk_text']}"
            )
    return context_list


# =============================
# Add file to index
# =============================

def add_file_to_index(file_path):
    index = initialize_pinecone()
    raw_text = read_txt_file_as_string(file_path)

    # Extract signal lines only
    signal_lines = [extract_signal(line) for line in raw_text.split('\n')]
    signal_lines = [line for line in signal_lines if line.strip()]
    signal_text = " ".join(signal_lines)

    if not signal_text:
        print("⚠️ No suspicious signals found in this file.")
        return None

    chunks = split_into_chunks(signal_text)
    vectors, embeddings = create_embeddings(chunks)
    upsert_chunks(index, chunks, vectors)

    print(f"✅ Done! '{file_path}' signals added to index '{INDEX_NAME}'.")
    return embeddings


# =============================
# Run Pipeline
# =============================

if __name__ == "__main__":
    index = initialize_pinecone()

    # Add new file
    embeddings = add_file_to_index("after_hours_anomalies.txt")


    print("\n\n")

    if embeddings:
        print("######## ✅ DETECTING A NORMAL LOG ########")
        contexts = search_index(index, embeddings, "normal_log.txt")

        
        for context in contexts:
            print("\n", context)
        print("\n\n")
        print("--------------------------------------------------")
        print("\n\n")
        print("######## ❌DETECTING AN UNUSUAL LOG ########")
        
        contexts = search_index(index, embeddings, "anomalies3.txt")
        

   
        for context in contexts:
            print("\n", context)

