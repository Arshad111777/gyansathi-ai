import streamlit as st
import tempfile, os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

st.title("📄 GyanSathi AI")
st.write("PDF upload karo aur kuch bhi poocho!")

# PDF Upload
uploaded_files = st.file_uploader(
    "PDF choose karo",
    accept_multiple_files=True,
    type="pdf"
)

if uploaded_files:
    all_chunks = []

    for file in uploaded_files:
        # Temp file mein save karo
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(file.read())
            tmp_path = f.name

        # Load + Chunk
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = splitter.split_documents(pages)
        all_chunks.extend(chunks)
        os.unlink(tmp_path)

    # Vector DB
    st.info(f"⏳ {len(all_chunks)} chunks process ho rahe hain...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_documents(all_chunks, embeddings)
    st.success("✅ PDF ready hai! Ab poocho kuch bhi.")

    # Chat
    query = st.text_input("Apna question likho:")

    if query:
        results = db.similarity_search(query, k=3)
        context = "\n".join([r.page_content for r in results])

        client = Groq(api_key="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")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }]
        )

        st.write("🤖 **Answer:**")
        st.write(response.choices[0].message.content)