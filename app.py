from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

# Step 1: PDF load karo
loader = PyPDFLoader("document.pdf")
pages = loader.load()
print(f"✅ Pages loaded: {len(pages)}")

# Step 2: Chunks banao
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(pages)
print(f"✅ Total chunks: {len(chunks)}")

# Step 3: Embed + Store
print("⏳ Embeddings ban rahi hain... thoda wait karo")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma.from_documents(chunks, embeddings)
print("✅ Vector DB ready!")

# Step 4: Question poocho
query = "how to secure a web application?"
results = db.similarity_search(query, k=3)
print(f"\n🔍 Retrieved {len(results)} chunks:")
for i, r in enumerate(results):
    print(f"\nChunk {i+1}:\n{r.page_content[:200]}")

# Step 5: Groq se answer lo
context = "\n".join([r.page_content for r in results])
client = Groq(api_key="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")

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {query}"
    }]
)
print(f"\n🤖 Answer:\n{response.choices[0].message.content}")