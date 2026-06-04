import streamlit as st
import os
import time
import json
import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

st.set_page_config(
    page_title="GyanSathi AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Styling ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #212121 !important;
    color: #ececec !important;
    font-family: 'Inter', sans-serif !important;
}


.stAppToolbar.st-emotion-cache-14vh5up.e1yxiy6j2 {
background: #212121!important;
}

.st-emotion-cache-fsmas1.e1lpckdq0 {
    display: none;
}

.st-emotion-cache-scp8yw.e1yxiy6j6 {
    display: none;
}

section.stMain.st-emotion-cache-4rsbii.eqt0gmo1 {
    max-width: 1000px;
    margin: 0 auto;
}

.st-emotion-cache-10p9htt.eelgd2m4 {
    width: 50px;
    height:50px;
    position: absolute;
    right: 10px;
    display:flex;
    justify-content: center;
    align-items: center;
    z-index:99999;
}



.st-emotion-cache-u1kubd h3 {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    background: linear-gradient(270deg, rgb(255, 75, 75), rgb(255, 140, 0), rgb(255, 200, 50), rgb(255, 140, 0), rgb(255, 75, 75)) !important;
    background-size: 300% 300% !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    animation: titleGlow 4s ease infinite !important;

}

[data-testid="stAppViewContainer"] > .main {
    background: #212121 !important;
}
.main .block-container {
    max-width: 760px !important;
    margin: 0 auto !important;
    padding: 2rem 1rem 6rem 1rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #171717 !important;
    border-right: 1px solid #2f2f2f !important;
}
[data-testid="stSidebar"] * {
    color: #ececec !important;
}
[data-testid="stSidebarContent"] {
    padding: 1rem 0.8rem !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #b4b4b4 !important;
    font-size: 0.82rem !important;
    text-align: left !important;
    padding: 0.5rem 0.8rem !important;
    border-radius: 6px !important;
    width: 100% !important;
    transition: all 0.15s !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #2f2f2f !important;
    color: #ffffff !important;
}

/* New chat button special */
.new-chat-btn > button {
    background: #2f2f2f !important;
    border: 1px solid #3f3f3f !important;
    color: #ececec !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 1rem !important;
    border-radius: 8px !important;
    width: 100% !important;
    margin-bottom: 1rem !important;
}
.new-chat-btn > button:hover {
    background: #3f3f3f !important;
}

/* Title */
@keyframes titleGlow {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
[data-testid="stHeadingWithActionElements"] h1 {
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    background: linear-gradient(270deg, rgb(255, 75, 75), rgb(255, 140, 0), rgb(255, 200, 50), rgb(255, 140, 0), rgb(255, 75, 75)) !important;
    background-size: 300% 300% !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    animation: titleGlow 4s ease infinite !important;
}
[data-testid="stHeaderActionElements"] { display: none !important; }

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid #2f2f2f !important;
    margin: 0.8rem 0 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.8rem 0 !important;
}
[data-testid="stChatMessage"] .stMarkdown {
    font-size: 0.95rem !important;
    line-height: 1.7 !important;
    color: #ececec !important;
}
[data-testid="stChatMessage"] h2 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #ececec !important;
    margin: 1rem 0 0.4rem 0 !important;
    padding-bottom: 4px !important;
    border-bottom: 1px solid #2f2f2f !important;
}
[data-testid="stChatMessage"] ul { padding-left: 1.2rem !important; }
[data-testid="stChatMessage"] li {
    margin: 0.25rem 0 !important;
    color: #d4d4d4 !important;
    font-size: 0.92rem !important;
}
[data-testid="stChatMessage"] strong {
    color: #ffffff !important;
    font-weight: 600 !important;
}

[data-testid="stBottomBlockContainer"] { padding: 1rem !important; }

/* Avatar */
[data-testid="chatAvatarIcon-user"] > div {
    background: #19c37d !important;
    color: #000 !important;
    font-weight: 700 !important;
}
[data-testid="chatAvatarIcon-assistant"] > div {
    background: #2f2f2f !important;
    color: #ececec !important;
}

/* Main buttons */
.stButton > button {
    background: #2f2f2f !important;
    color: #d4d4d4 !important;
    border: 1px solid #3f3f3f !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    padding: 0.45rem 0.8rem !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #3f3f3f !important;
    border-color: #565656 !important;
    color: #ffffff !important;
}

/* Chat input glow */
@property --glow-deg {
    syntax: "<angle>";
    inherits: true;
    initial-value: -90deg;
}
@property --clr-1 { syntax: "<color>"; inherits: true; initial-value: rgb(255, 75, 75); }
@property --clr-2 { syntax: "<color>"; inherits: true; initial-value: rgb(255, 140, 0); }
@property --clr-3 { syntax: "<color>"; inherits: true; initial-value: rgb(255, 75, 75); }
@property --clr-4 { syntax: "<color>"; inherits: true; initial-value: rgb(200, 30, 30); }

@keyframes glowRotate {
    0%   { --glow-deg: -90deg; }
    100% { --glow-deg: 270deg; }
}

[data-testid="stChatInput"] {
    --gradient-glow: var(--clr-1), var(--clr-2), var(--clr-3), var(--clr-4), var(--clr-1);
    background: linear-gradient(#2f2f2f 0 0) padding-box,
                conic-gradient(from var(--glow-deg), var(--gradient-glow)) border-box !important;
    border: 2px solid transparent !important;
    border-radius: 12px !important;
    position: relative !important;
    isolation: isolate !important;
    animation: glowRotate 4s infinite linear !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #ececec !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #666 !important; }

[data-testid="stBottom"] {
    background: linear-gradient(to top, #212121 80%, transparent) !important;
    padding-bottom: 1rem !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #2f2f2f !important;
    border: 1px solid #3f3f3f !important;
    border-radius: 8px !important;
    color: #d4d4d4 !important;
    font-size: 0.82rem !important;
}

/* Alerts */
[data-testid="stAlert"] {
    background: #2a2a2a !important;
    border: 1px solid #3f3f3f !important;
    border-radius: 8px !important;
    color: #b4b4b4 !important;
    font-size: 0.85rem !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: #2a2a2a !important;
    border: 1px solid #2f2f2f !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] p { color: #888 !important; font-size: 0.8rem !important; }

/* Toggle */
[data-testid="stToggle"] label { color: #b4b4b4 !important; font-size: 0.82rem !important; }

/* Caption */
.stCaption { color: #666 !important; font-size: 0.78rem !important; }

.st-emotion-cache-hzygls { background: unset !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #212121; }
::-webkit-scrollbar-thumb { background: #3f3f3f; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #565656; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────
PDF_FOLDER = "pdfs"

LANGUAGES = {
    "🇬🇧 English": "ALWAYS respond in English only.",
    "🇮🇳 Hinglish": "ALWAYS respond in Hinglish — mix Hindi and English. NEVER use pure Hindi words like 'mahatvapoorn'.",
    "🇮🇳 Hindi": "ALWAYS respond in pure Hindi.",
}

# ─── Session State Init ───────────────────────────────────
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}  # {chat_id: {"title": "...", "messages": []}}

if "current_chat_id" not in st.session_state:
    new_id = str(uuid.uuid4())[:8]
    st.session_state.all_chats[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id

if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False

if "ready_msg_shown" not in st.session_state:
    st.session_state.ready_msg_shown = False

# ─── Helper Functions ─────────────────────────────────────
def get_current_messages():
    return st.session_state.all_chats[st.session_state.current_chat_id]["messages"]

def add_message(role, content):
    chat = st.session_state.all_chats[st.session_state.current_chat_id]
    chat["messages"].append({"role": role, "content": content})
    # First user message se title set karo
    if role == "user" and chat["title"] == "New Chat":
        chat["title"] = content[:30] + "..." if len(content) > 30 else content

def new_chat():
    new_id = str(uuid.uuid4())[:8]
    st.session_state.all_chats[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id
    st.session_state.quiz_active = False

# ─── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 GyanSathi AI")
    st.divider()

    # New Chat button
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("✏️ New Chat"):
        new_chat()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat history list
    st.markdown("**🕐 Recent Chats**")

    # Reverse order — latest pehle
    for chat_id in reversed(list(st.session_state.all_chats.keys())):
        chat = st.session_state.all_chats[chat_id]
        is_active = chat_id == st.session_state.current_chat_id
        title = chat["title"]
        label = f"💬 {title}" if is_active else f"🕐 {title}"

        if st.button(label, key=f"chat_{chat_id}"):
            st.session_state.current_chat_id = chat_id
            st.session_state.quiz_active = False
            st.rerun()

    st.divider()

    # Clear current chat
    if st.button("🗑️ Clear Current Chat"):
        st.session_state.all_chats[st.session_state.current_chat_id]["messages"] = []
        st.session_state.all_chats[st.session_state.current_chat_id]["title"] = "New Chat"
        st.rerun()

# ─── Main Header ──────────────────────────────────────────
st.title("🤖 GyanSathi AI")
st.caption("Har Subject, Har Semester, Aapka Smart Saathi.")

col1, col2, col3 = st.columns([3, 2, 1])
with col2:
    selected_lang = st.selectbox(
        "lang",
        options=list(LANGUAGES.keys()),
        index=0,
        label_visibility="collapsed"
    )
with col3:
    quiz_mode = st.toggle("🧠 Quiz")
with col1:
    st.caption(f"Chat: {st.session_state.all_chats[st.session_state.current_chat_id]['title'][:25]}")

st.divider()

# ─── PDF Load ─────────────────────────────────────────────
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

if not pdf_files:
    st.warning("⚠️ Koi PDF nahi mili. Admin se upload karwao.")
    st.stop()

@st.cache_resource
def load_db():
    all_chunks = []
    book_chunks = []
    pyq_chunks = []

    for pdf in pdf_files:
        path = os.path.join(PDF_FOLDER, pdf)
        loader = PyPDFLoader(path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_documents(pages)

        for chunk in chunks:
            filename = pdf.lower()
            if filename.startswith("bca") or "question" in filename or "pyq" in filename:
                chunk.metadata["type"] = "pyq"
                pyq_chunks.append(chunk)
            else:
                chunk.metadata["type"] = "book"
                book_chunks.append(chunk)
            all_chunks.append(chunk)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # FAISS ke liye alag alag index banao
    main_db = FAISS.from_documents(all_chunks, embeddings)
    book_db = FAISS.from_documents(book_chunks, embeddings) if book_chunks else None
    pyq_db = FAISS.from_documents(pyq_chunks, embeddings) if pyq_chunks else None

    return main_db, book_db, pyq_db

with st.spinner("⏳ Knowledge base load ho rahi hai..."):
    main_db, book_db, pyq_db = load_db()

book_count = sum(1 for f in pdf_files if not f.lower().startswith("bca"))
pyq_count = sum(1 for f in pdf_files if f.lower().startswith("bca"))

if not st.session_state.ready_msg_shown:
    msg = st.success(f"✅ Ready! 📚 {book_count} Book | 📝 {pyq_count} Question Papers loaded.")
    time.sleep(2)
    msg.empty()
    st.session_state.ready_msg_shown = True

# ─── Quick Actions ────────────────────────────────────────
if "English" in selected_lang:
    q1 = "Which questions are repeated across all three papers? List them with answers."
    q2 = "Which topics are most important for exam? Which came again and again?"
    q3 = "List all important topics that can come in exam."
elif "Hindi" in selected_lang:
    q1 = "Teeno papers mein konse questions repeat hue hain? List karo with answers."
    q2 = "Konse topics sabse zyada important hain exam ke liye?"
    q3 = "Saare important topics list karo jo exam mein aa sakte hain."
else:
    q1 = "Konse questions teeno papers mein repeat hue hain? List karo with answers."
    q2 = "Konse topics sabse zyada important hain exam ke liye? Jo baar baar aaye hain."
    q3 = "Saare important topics list karo jo exam mein aa sakte hain."

qcol1, qcol2, qcol3 = st.columns(3)
with qcol1:
    if st.button("🔁 Repeat Questions"):
        st.session_state.quick_query = q1
with qcol2:
    if st.button("⭐ Most Important"):
        st.session_state.quick_query = q2
with qcol3:
    if st.button("📋 Full Syllabus"):
        st.session_state.quick_query = q3

st.divider()

# ─── Quiz Mode ────────────────────────────────────────────
if quiz_mode and not st.session_state.quiz_active:
    st.session_state.quiz_active = True
    search_db = pyq_db if pyq_db else main_db
    results = search_db.similarity_search("cyber security exam questions", k=4)
    context = "\n".join([r.page_content for r in results])

    client = Groq(api_key=st.secrets["GROQ_KEY"])
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": f"You are GyanSathi AI in Quiz Mode. {LANGUAGES[selected_lang]} Ask 1 MCQ from past exam questions. After answer, say correct/wrong, explain briefly, then next question."},
            {"role": "user", "content": f"Past exam questions:\n{context}\n\nAsk 1 MCQ question."}
        ]
    )
    quiz_q = response.choices[0].message.content
    add_message("assistant", "🧠 **Quiz Mode ON!**\n\n" + quiz_q)
elif not quiz_mode:
    st.session_state.quiz_active = False

# ─── Display Messages ─────────────────────────────────────
current_messages = get_current_messages()
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── Handle Quick Query ───────────────────────────────────
query = None
if "quick_query" in st.session_state:
    query = st.session_state.quick_query
    del st.session_state.quick_query

# ─── Chat Input ───────────────────────────────────────────
placeholder = "Quiz ka answer do..." if quiz_mode else "Poocho — theory, repeat questions, important topics..."
user_input = st.chat_input(placeholder)
if user_input:
    query = user_input

# ─── Process Query ────────────────────────────────────────
if query:
    with st.chat_message("user"):
        st.write(query)
    add_message("user", query)

    identity_keywords = ["kaun ho", "kaun hain", "kya ho", "who are you", "introduce", "parichay"]
    is_identity = any(kw in query.lower() for kw in identity_keywords)

    if is_identity:
        answer = "Main **GyanSathi AI** hun! 🤖 Aapke **Cyber Security** knowledge aur exam preparation mein help karna mera kaam hai. Poocho jo bhi chahte ho!"
        sources_text = ""
    else:
        # FAISS alag alag DBs se search karo
        book_results = book_db.similarity_search(query, k=3) if book_db else []
        pyq_results = pyq_db.similarity_search(query, k=4) if pyq_db else []

        book_context = "\n".join([r.page_content for r in book_results])
        pyq_context = "\n".join([r.page_content for r in pyq_results])

        # Sources
        sources = []
        for r in book_results + pyq_results:
            page = r.metadata.get("page", None)
            source = r.metadata.get("source", "")
            filename = os.path.basename(source) if source else "PDF"
            doc_type = r.metadata.get("type", "")
            tag = "📚 Book" if doc_type == "book" else "📝 PYQ"
            if page is not None:
                sources.append(f"{tag}: {filename} — Page {page + 1}")
        sources_text = "\n".join(list(dict.fromkeys(sources)))

        lang_instruction = LANGUAGES[selected_lang]
        repeat_keywords = ["repeat", "repeated", "baar baar", "important", "most asked", "syllabus", "konse"]
        is_repeat_query = any(kw in query.lower() for kw in repeat_keywords)

        if quiz_mode:
            system_content = f"You are GyanSathi AI in Quiz Mode. {lang_instruction} Check answer, say correct/wrong, explain briefly, then ask next MCQ."
            full_context = f"Past exam questions:\n{pyq_context}"
        elif is_repeat_query:
            system_content = f"""You are GyanSathi AI — Exam Expert.
{lang_instruction}
Find repeated questions across papers and list with answers.

FORMAT:
## 🔁 Repeat Questions
(list with ⭐⭐⭐ = 3 papers, ⭐⭐ = 2 papers)

## 📖 Their Answers
(brief answers)

## ⚠️ Exam Tip"""
            full_context = f"BOOK THEORY:\n{book_context}\n\nPAST EXAM PAPERS:\n{pyq_context}"
        else:
            system_content = f"""You are GyanSathi AI — Cyber Security mentor.
{lang_instruction}

FORMAT:
## 📖 Theory
## 📝 Previously Asked In Exam
## ⭐ Exam Tip

RULES: Only Cyber Security topics. Ignore preface/dedication."""
            full_context = f"BOOK THEORY:\n{book_context}\n\nPAST EXAM QUESTIONS:\n{pyq_context}"

        client = Groq(api_key=st.secrets["GROQ_KEY"])
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"Context:\n{full_context}\n\nQuestion: {query}"}
            ]
        )
        answer = response.choices[0].message.content

    with st.chat_message("assistant"):
        st.markdown(answer)
        if not is_identity and sources_text and not quiz_mode:
            with st.expander("📚 Sources"):
                st.caption(sources_text)

    full_answer = answer + (f"\n\nSources:\n{sources_text}" if sources_text and not quiz_mode else "")
    add_message("assistant", full_answer)