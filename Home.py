import streamlit as st
import os
import time
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

st.set_page_config(
    page_title="GyanSathi AI",
    page_icon="🤖",
    initial_sidebar_state="collapsed"
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

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

[data-testid="stAppViewContainer"] > .main {
    background: #212121 !important;
}
.main .block-container {
    max-width: 760px !important;
    margin: 0 auto !important;
    padding: 2rem 1rem 6rem 1rem !important;
}

/* Title */
/* ── Animated Gradient Title ── */
@keyframes titleGlow {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

[data-testid="stHeadingWithActionElements"] h1 {
    font-size: 3.8rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    
    /* Animated gradient text */
    background: linear-gradient(
        270deg,
        rgb(255, 75, 75),
        rgb(255, 140, 0),
        rgb(255, 200, 50),
        rgb(255, 140, 0),
        rgb(255, 75, 75)
    ) !important;
    background-size: 300% 300% !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    animation: titleGlow 4s ease infinite !important;
}

/* Hide anchor link icon */
[data-testid="stHeaderActionElements"] {
    display: none !important;
}


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

/* Headings inside answers */
[data-testid="stChatMessage"] h2 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #ececec !important;
    margin: 1rem 0 0.4rem 0 !important;
    padding-bottom: 4px !important;
    border-bottom: 1px solid #2f2f2f !important;
}
[data-testid="stChatMessage"] ul {
    padding-left: 1.2rem !important;
}
[data-testid="stChatMessage"] li {
    margin: 0.25rem 0 !important;
    color: #d4d4d4 !important;
    font-size: 0.92rem !important;
}
[data-testid="stChatMessage"] strong {
    color: #ffffff !important;
    font-weight: 600 !important;
}

[data-testid="stBottomBlockContainer"] {
    padding: 1rem!important;
}

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

/* Buttons */
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

/* Chat input */
/* ── Animated Conic Glow - Gemini Style ── */
@property --glow-deg {
    syntax: "<angle>";
    inherits: true;
    initial-value: -90deg;
}
@property --clr-1 {
    syntax: "<color>";
    inherits: true;
    initial-value: rgb(255, 75, 75);
}
@property --clr-2 {
    syntax: "<color>";
    inherits: true;
    initial-value: rgb(255, 140, 0);
}
@property --clr-3 {
    syntax: "<color>";
    inherits: true;
    initial-value: rgb(255, 75, 75);
}
@property --clr-4 {
    syntax: "<color>";
    inherits: true;
    initial-value: rgb(200, 30, 30);
}

@keyframes glowRotate {
    0%   { --glow-deg: -90deg; }
    100% { --glow-deg: 270deg; }
}

[data-testid="stChatInput"] {
    --gradient-glow: var(--clr-1), var(--clr-2), var(--clr-3), var(--clr-4), var(--clr-1);
    --glow-size: 10px;
    --border-width: 2px;

    background: linear-gradient(#2f2f2f 0 0) padding-box,
                conic-gradient(from var(--glow-deg), var(--gradient-glow)) border-box !important;

    border: var(--border-width) solid transparent !important;
    border-radius: 12px !important;
    position: relative !important;
    isolation: isolate !important;
    animation: glowRotate 4s infinite linear !important;
}

/* Outer blurred glow */
[data-testid="stChatInput"]::after {
    content: "" !important;
    position: absolute !important;
    z-index: -1 !important;
    inset: -4px !important;
    border-radius: 14px !important;
    background: conic-gradient(from var(--glow-deg), var(--gradient-glow)) !important;
    filter: blur(var(--glow-size)) !important;
    opacity: 0.25 !important;
    animation: glowRotate 4s infinite linear !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #ececec !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #666 !important;
}

/* Bottom fixed area background */
[data-testid="stBottom"] {
    background: linear-gradient(to top, #212121 80%, transparent) !important;
    padding-bottom: 1rem !important;
}

/* Bottom gradient */
[data-testid="stBottom"] {
    background: transparent !important;
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
[data-testid="stExpander"] p {
    color: #888 !important;
    font-size: 0.8rem !important;
}

/* Toggle */
[data-testid="stToggle"] label {
    color: #b4b4b4 !important;
    font-size: 0.82rem !important;
}

/* Caption */
.stCaption {
    color: #666 !important;
    font-size: 0.78rem !important;
}

.st-emotion-cache-hzygls{
    background: unset !important;
}

/* Custom Styling issues fixing */

.st-emotion-cache-128upt6.eqt0gmo3 {
    background: transparent!important;
}

.st-emotion-cache-6mn6c9{
    background: #2f2f2f !important;
}

[data-testid="stChatMessage"] h2 {
    margin-top: 0!important;
    padding-top: 0!important;
    font-size: 2rem!important;
}


/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #212121; }
::-webkit-scrollbar-thumb { background: #3f3f3f; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #565656; }
</style>
""", unsafe_allow_html=True)



# ─── Constants ───────────────────────────────────────────
PDF_FOLDER = "pdfs"
CHAT_HISTORY_FILE = "chat_history.json"

LANGUAGES = {
    "🇬🇧 English": "ALWAYS respond in English only.",
    "🇮🇳 Hinglish": "ALWAYS respond in Hinglish — mix Hindi and English. Example: 'Cyber Security ek important field hai jo digital data ko protect karti hai.' NEVER use pure Hindi words like 'mahatvapoorn' — use simple Hindi only.",
    "🇮🇳 Hindi": "ALWAYS respond in pure Hindi.",
}

# ─── Chat History ─────────────────────────────────────────
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_chat_history(messages):
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=True, indent=2)

# ─── Header ───────────────────────────────────────────────
st.title("🤖 GyanSathi AI")
st.caption("Har Subject, Har Semester, Aapka Smart Saathi.")

col1, col2, col3 = st.columns([3, 2, 1])
with col2:
    selected_lang = st.selectbox(
        "🌐 Language",
        options=list(LANGUAGES.keys()),
        index=0,
        label_visibility="collapsed"
    )
with col3:
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        save_chat_history([])
        st.rerun()
with col1:
    quiz_mode = st.toggle("🧠 Quiz Mode")

st.divider()

# ─── PDF Load with Tags ───────────────────────────────────
pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

if not pdf_files:
    st.warning("⚠️ Koi PDF nahi mili. Admin se upload karwao.")
    st.stop()

@st.cache_resource
def load_db():
    all_chunks = []
    for pdf in pdf_files:
        path = os.path.join(PDF_FOLDER, pdf)
        loader = PyPDFLoader(path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(pages)

        # Tag karo — book hai ya PYQ
        for chunk in chunks:
            filename = pdf.lower()
            if filename.startswith("bca") or "question" in filename or "pyq" in filename:
                chunk.metadata["type"] = "pyq"
                chunk.metadata["paper"] = pdf
            else:
                chunk.metadata["type"] = "book"

        all_chunks.extend(chunks)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # db = Chroma.from_documents(all_chunks, embeddings)
    db = FAISS.from_documents(all_chunks, embeddings)
    return db

with st.spinner("⏳ Knowledge base load ho rahi hai..."):
    db = load_db()

# PDF count dikhao
book_count = sum(1 for f in pdf_files if not f.lower().startswith("bca"))
pyq_count = sum(1 for f in pdf_files if f.lower().startswith("bca"))

if "ready_msg_shown" not in st.session_state:
    msg = st.success(
        f"✅ Ready! 📚 {book_count} Book | 📝 {pyq_count} Question Papers loaded."
    )

    time.sleep(3)
    msg.empty()

    st.session_state.ready_msg_shown = True
# ─── Session State ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False

# ─── Quick Action Buttons ─────────────────────────────────

st.write("**Quick Actions:**")
qcol1, qcol2, qcol3 = st.columns(3)

# Language ke according query set karo
if "English" in selected_lang:
    q1 = "Which questions are repeated across all three papers? List them with answers."
    q2 = "Which topics are most important for exam? Which came again and again?"
    q3 = "List all important topics that can come in exam."
elif "Hindi" in selected_lang:
    q1 = "Teeno papers mein konse questions repeat hue hain? List karo with answers."
    q2 = "Konse topics sabse zyada important hain exam ke liye? Jo baar baar aaye hain."
    q3 = "Saare important topics list karo jo exam mein aa sakte hain."
else:  # Hinglish default
    q1 = "Konse questions teeno papers mein repeat hue hain? List karo with answers."
    q2 = "Konse topics sabse zyada important hain exam ke liye? Jo baar baar aaye hain."
    q3 = "Saare important topics list karo jo exam mein aa sakte hain."

with qcol1:
    if st.button("🔁 Repeat Questions"):
        st.session_state.quick_query = q1
with qcol2:
    if st.button("⭐ Most Important"):
        st.session_state.quick_query = q2
with qcol3:
    if st.button("📋 Full Syllabus"):
        st.session_state.quick_query = q3



# st.write("**Quick Actions:**")
# qcol1, qcol2, qcol3 = st.columns(3)

# with qcol1:
#     if st.button("🔁 Repeat Questions"):
#         st.session_state.quick_query = "Konse questions teeno papers mein repeat hue hain? List karo with answers."
# with qcol2:
#     if st.button("⭐ Most Important"):
#         st.session_state.quick_query = "Konse topics sabse zyada important hain exam ke liye? Jo baar baar aaye hain."
# with qcol3:
#     if st.button("📋 Full Syllabus"):
#         st.session_state.quick_query = "Saare important topics list karo jo exam mein aa sakte hain."

# ─── Quiz Mode ────────────────────────────────────────────
if quiz_mode and not st.session_state.quiz_active:
    st.session_state.quiz_active = True
    results = db.similarity_search("cyber security exam questions", k=4,
                                   filter={"type": "pyq"})
    context = "\n".join([r.page_content for r in results])

    client = Groq(api_key=st.secrets["GROQ_KEY"])
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": f"You are GyanSathi AI in Quiz Mode. {LANGUAGES[selected_lang]} Ask 1 MCQ from past exam questions. After answer, say correct/wrong, explain briefly, then next question."
            },
            {
                "role": "user",
                "content": f"Past exam questions:\n{context}\n\nAsk 1 MCQ question."
            }
        ]
    )
    quiz_q = response.choices[0].message.content
    st.session_state.messages.append({
        "role": "assistant",
        "content": "🧠 **Quiz Mode ON! Past exam questions se poocha jayega.**\n\n" + quiz_q
    })
    save_chat_history(st.session_state.messages)
elif not quiz_mode:
    st.session_state.quiz_active = False

# ─── Display Messages ─────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── Handle Quick Query ───────────────────────────────────
if "quick_query" in st.session_state:
    query = st.session_state.quick_query
    del st.session_state.quick_query
else:
    query = None

# ─── Chat Input ───────────────────────────────────────────
placeholder = "Quiz ka answer do..." if quiz_mode else "Ask — theory, repeat questions, important topics..."
user_input = st.chat_input(placeholder)

if user_input:
    query = user_input

# ─── Process Query ────────────────────────────────────────
if query:
    with st.chat_message("user"):
        st.write(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # Identity check
    identity_keywords = ["kaun ho", "kaun hain", "kya ho", "who are you", "introduce", "parichay"]
    is_identity = any(kw in query.lower() for kw in identity_keywords)

    if is_identity:
        answer = "Main **GyanSathi AI** hun! 🤖 Aapke **Cyber Security** knowledge aur exam preparation mein help karna mera kaam hai. Poocho jo bhi chahte ho!"
        sources_text = ""

    else:
        # Book se theory
        book_results = db.similarity_search(query, k=3, filter={"type": "book"})
        book_context = "\n".join([r.page_content for r in book_results])
        
        # PYQ se related questions
        pyq_results = db.similarity_search(query, k=4, filter={"type": "pyq"})
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

        # Repeat/important question detect karo
        repeat_keywords = ["repeat", "repeated", "baar baar", "important", "most asked", "syllabus", "konse"]
        is_repeat_query = any(kw in query.lower() for kw in repeat_keywords)

        if quiz_mode:
            system_content = f"""You are GyanSathi AI in Quiz Mode.
{lang_instruction}
Check answer, say correct/wrong, explain briefly, then ask next MCQ from past papers."""

            full_context = f"Past exam questions:\n{pyq_context}"

        elif is_repeat_query:
            system_content = f"""You are GyanSathi AI — Exam Expert.
{lang_instruction}

Analyze the past exam papers provided and:
1. Find questions that appear in MULTIPLE papers (repeat questions)
2. List them clearly with answers from book context
3. Mark importance level

FORMAT:
## 🔁 Repeat Questions (Multiple Papers Mein Aaye)
(list with ⭐⭐⭐ = 3 papers, ⭐⭐ = 2 papers)

## 📖 Unke Answers
(brief answers)

## ⚠️ Exam Tip
(kya prepare karna chahiye)"""

            full_context = f"BOOK THEORY:\n{book_context}\n\nPAST EXAM PAPERS:\n{pyq_context}"

        else:
            system_content = f"""You are GyanSathi AI — Cyber Security mentor.
{lang_instruction}

FORMAT:
## 📖 Theory
(book se clear explanation)

## 📝 Exam Mein Kaise Aaya
(PYQ se relevant questions mention karo)

## ⭐ Exam Tip
(short important tip)

RULES:
- Sirf Cyber Security topics answer karo
- Preface/dedication ignore karo
- Agar content na mile: "Is topic par information nahi hai.\""""

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

    # Answer dikhao
    with st.chat_message("assistant"):
        st.markdown(answer)
        if not is_identity and sources_text and not quiz_mode:
            with st.expander("📚 Sources dekho"):
                st.caption(sources_text)

    full_answer = answer + (f"\n\n📚 Sources:\n{sources_text}" if sources_text and not quiz_mode else "")
    st.session_state.messages.append({"role": "assistant", "content": full_answer})
    save_chat_history(st.session_state.messages)