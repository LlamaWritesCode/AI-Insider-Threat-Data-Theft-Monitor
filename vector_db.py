from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone

from langchain_community.llms import OpenAI
from langchain_community.document_loaders import TextLoader
from pinecone import Pinecone, ServerlessSpec

from convertcs import read_txt_file_as_string
import os
api_key = os.getenv("PINECONE_API_KEY")
api_key2 = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=api_key)


if not pc.has_index("ibm-hack"):
    pc.create_index(
        name="ibm-hack",
        dimension=1536,
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        embed={
            "model": "llama-text-embed-v2",   # or the model your semantic search requires
            "field_map": {"text": "chunk_text"}
        }
    )

    
index = pc.Index(host ="https://ibm-hack-lgywj80.svc.aped-4627-b74a.pinecone.io")   
print("Connecting to Pinecone index...")

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

# Load your log file as text
data = read_txt_file_as_string("anomalies.txt")

# Split into overlapping chunks
chunks = split_into_chunks(data, max_words=50, overlap=30)

# Show chunks for verification
#print("\n==== CHUNKS ====\n")
#for idx, chunk in enumerate(chunks, start=1):
   #print(f"[Chunk {idx}]:\n{chunk}\n")

# Next steps: Embed & store with FAISS if needed.
# For example:
embeddings = OpenAIEmbeddings(openai_api_key=api_key2)
vectors = embeddings.embed_documents(chunks)
print(f"✅ Created {len(vectors)} embeddings.")

records = []
for i, chunk in enumerate(chunks):
    records.append({
        "_id": f"resume-chunk-{i}",
        "embedding": vectors[i],  # ✅ Add this!
        "chunk_text": chunk,
        "category": "resume"
    })
index.upsert(
    vectors=[
        (r["_id"], r["embedding"], {"chunk_text": r["chunk_text"], "category": r["category"]})
        for r in records
    ],
    namespace="ns1"
)

file = read_txt_file_as_string("normal_log.txt")

query_vector = embeddings.embed_query(file)


# Step 2: Search index by vector (not by raw text)

results = index.query(
    vector=query_vector,
    top_k=3,
    namespace="ns1",
    include_metadata=True
)

print(results)
"""
context_list=[]
if not results['result']['hits']:
    print("no results")
else:
    for hit in results['result']['hits']:
            
        #print(f"Chunk {hit['_id'][-1]} (score: {hit['_score']}):  Content of chunk {hit['_id'][-1]} : {hit['fields']['chunk_text']}")
        context_list.append(f"Chunk {hit['_id'][-1]} (score: {hit['_score']}):  Content of chunk {hit['_id'][-1]} : {hit['fields']['chunk_text']}")
        
#print(records)
"""