import streamlit as st
import os
import time
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f0f0f !important; color: #e8e8e8 !important;
    font-family: 'Sora', sans-serif !important;
}


.stAppToolbar.st-emotion-cache-14vh5up.e1yxiy6j2 {
background: #0f0f0f !important;
}

section.stMain.st-emotion-cache-4rsbii.eqt0gmo1 {
    max-width: 900px;
    margin: 0 auto;
}

[data-testid="stAppViewContainer"] > .main { background: #0f0f0f !important; }
.main .block-container { max-width: 720px !important; margin: 0 auto !important; padding: 2rem 1.5rem 7rem 1.5rem !important; }

/* SIDEBAR */

[data-testid="stSidebarContent"] { padding: 0 !important; background: #0f0f0f !important; border-right: 1px solid #242424 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important; color: #888 !important;
    font-size: 0.8rem !important; text-align: left !important; padding: 0.45rem 0.7rem !important;
    border-radius: 6px !important; width: 100% !important; transition: all 0.15s !important;
    white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important;
    font-family: 'Sora', sans-serif !important;
}
[data-testid="stSidebar"] .stButton > button:hover { background: #161616 !important; color: #fff !important; }

/* TITLE */
@keyframes titleGlow {
    0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; }
}
[data-testid="stHeadingWithActionElements"] h1 {
    font-size: 2rem !important; font-weight: 700 !important; letter-spacing: -0.5px !important;
    background: linear-gradient(270deg, rgb(255,75,75), rgb(255,140,0), rgb(255,200,50), rgb(255,140,0), rgb(255,75,75)) !important;
    background-size: 300% 300% !important; -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important; background-clip: text !important;
    animation: titleGlow 4s ease infinite !important;
}
[data-testid="stHeaderActionElements"] { display: none !important; }
hr { border: none !important; border-top: 1px solid #1e1e1e !important; margin: 0.8rem 0 !important; }

/* CHAT */
[data-testid="stChatMessage"] { background: transparent !important; border: none !important; padding: 0.8rem 0 !important; }
[data-testid="stChatMessage"] .stMarkdown { font-size: 0.92rem !important; line-height: 1.75 !important; color: #e0e0e0 !important; }
[data-testid="stChatMessage"] h2 { font-size: 0.95rem !important; font-weight: 600 !important; color: #ececec !important; margin: 1rem 0 0.4rem 0 !important; padding-bottom: 4px !important; border-bottom: 1px solid #1e1e1e !important; }
[data-testid="stChatMessage"] ul { padding-left: 1.2rem !important; }
[data-testid="stChatMessage"] li { margin: 0.25rem 0 !important; color: #c8c8c8 !important; font-size: 0.88rem !important; }
[data-testid="stChatMessage"] strong { color: #fff !important; font-weight: 600 !important; }
[data-testid="stBottomBlockContainer"] { padding: 1rem !important; }
[data-testid="chatAvatarIcon-user"] > div { background: linear-gradient(135deg, rgb(255,75,75), rgb(255,140,0)) !important; color: #000 !important; font-weight: 700 !important; }
[data-testid="chatAvatarIcon-assistant"] > div { background: #1a1a1a !important; color: rgb(255,140,0) !important; border: 1px solid #2a2a2a !important; }

/* BUTTONS */
.stButton > button { background: #141414 !important; color: #aaa !important; border: 1px solid #222 !important; border-radius: 8px !important; font-size: 0.78rem !important; font-family: 'Sora', sans-serif !important; padding: 0.45rem 0.8rem !important; transition: all 0.2s ease !important; width: 100% !important; }
.stButton > button:hover { background: #1e1e1e !important; border-color: #333 !important; color: #fff !important; transform: translateY(-1px) !important; }

/* GLOW INPUT */
@property --glow-deg { syntax: "<angle>"; inherits: true; initial-value: -90deg; }
@property --clr-1 { syntax: "<color>"; inherits: true; initial-value: rgb(255, 75, 75); }
@property --clr-2 { syntax: "<color>"; inherits: true; initial-value: rgb(255, 140, 0); }
@property --clr-3 { syntax: "<color>"; inherits: true; initial-value: rgb(255, 75, 75); }
@property --clr-4 { syntax: "<color>"; inherits: true; initial-value: rgb(200, 30, 30); }
@keyframes glowRotate { 0% { --glow-deg: -90deg; } 100% { --glow-deg: 270deg; } }
[data-testid="stChatInput"] {
    --gradient-glow: var(--clr-1), var(--clr-2), var(--clr-3), var(--clr-4), var(--clr-1);
    background: linear-gradient(#141414 0 0) padding-box, conic-gradient(from var(--glow-deg), var(--gradient-glow)) border-box !important;
    border: 2px solid transparent !important; border-radius: 14px !important; position: relative !important; isolation: isolate !important; animation: glowRotate 4s infinite linear !important;
    padding: 1px 2px !important;
}
[data-testid="stChatInput"] textarea { background: transparent !important; color: #e8e8e8 !important; font-size: 0.92rem !important; font-family: 'Sora', sans-serif !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #444 !important; }
[data-testid="stBottom"] { background: linear-gradient(to top, #0f0f0f 75%, transparent) !important; padding-bottom: 1rem !important; }

/* MISC */
[data-testid="stSelectbox"] > div > div { background: #141414 !important; border: 1px solid #222 !important; border-radius: 8px !important; color: #ccc !important; font-size: 0.8rem !important; font-family: 'Sora', sans-serif !important; }
[data-testid="stToggle"] label { color: #888 !important; font-size: 0.8rem !important; }
[data-testid="stAlert"] { background: #141414 !important; border: 1px solid #222 !important; border-radius: 10px !important; color: #aaa !important; font-size: 0.82rem !important; }
[data-testid="stExpander"] { background: #141414 !important; border: 1px solid #1e1e1e !important; border-radius: 8px !important; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] p { color: #666 !important; font-size: 0.78rem !important; }
.stCaption { color: #555 !important; font-size: 0.75rem !important; }
.st-emotion-cache-hzygls { background: unset !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a3a; }

/* Subject badge */
.subject-badge {
    display: inline-block; background: #1a1a1a; border: 1px solid #2a2a2a;
    color: rgb(255,140,0); padding: 2px 10px; border-radius: 20px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px;
}

/* Custom Styling */

.st-emotion-cache-jchovf:focus-within{
    border:none !important;
}

.st-emotion-cache-jchovf{
    border: none !important;
}

.st-emotion-cache-6mn6c9 {
    background: rgb(38, 39, 48);
}

[data-testid="stChatInput"] textarea {
    background: rgb(38, 39, 48) !important;
}

._profileContainer_gzau3_53 {
    display: none !important;
}

.st-emotion-cache-128upt6 {
    background: transparent!important;
}

.st-emotion-cache-scp8yw{
    display: none !important;
}

.st-emotion-cache-fsmas1{
    display: none !important;
}

.st-emotion-cache-10p9htt {
    position: absolute;
    right: -8px;
    top: -5px;
    width: 50px;
    height: 50px;
    z-index: 9999999;
}

</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────
PDF_FOLDER = "pdfs"
LANGUAGES = {
    "🇬🇧 English": "ALWAYS respond in English only.",
    "🇮🇳 Hinglish": "ALWAYS respond in Hinglish — mix Hindi and English. NEVER use pure Hindi words like 'mahatvapoorn'.",
    "🇮🇳 Hindi": "ALWAYS respond in pure Hindi.",
}

# ─── Session State ────────────────────────────────────────
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}
if "current_chat_id" not in st.session_state:
    new_id = str(uuid.uuid4())[:8]
    st.session_state.all_chats[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "ready_msg_shown" not in st.session_state:
    st.session_state.ready_msg_shown = False

def get_current_messages():
    return st.session_state.all_chats[st.session_state.current_chat_id]["messages"]

def add_message(role, content):
    chat = st.session_state.all_chats[st.session_state.current_chat_id]
    chat["messages"].append({"role": role, "content": content})
    if role == "user" and chat["title"] == "New Chat":
        chat["title"] = content[:28] + "..." if len(content) > 28 else content

def new_chat():
    new_id = str(uuid.uuid4())[:8]
    st.session_state.all_chats[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id
    st.session_state.quiz_active = False

# ─── Dynamic Subject DB Loader ────────────────────────────
@st.cache_resource
def load_all_subject_dbs():
    """
    pdfs/ ke andar har subfolder ek subject hai.
    Har subject ke liye alag book_db aur pyq_db banao.
    Returns: { "subject_name": {"book": FAISS|None, "pyq": FAISS|None} }
    """
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        return {}

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    subject_dbs = {}

    subjects = [d for d in os.listdir(PDF_FOLDER)
                if os.path.isdir(os.path.join(PDF_FOLDER, d))]

    # Root PDFs bhi handle karo (backward compatibility)
    root_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    if root_pdfs:
        subjects_with_root = ["_general"] + subjects
    else:
        subjects_with_root = subjects

    for subject in subjects_with_root:
        if subject == "_general":
            folder = PDF_FOLDER
            pdfs = root_pdfs
        else:
            folder = os.path.join(PDF_FOLDER, subject)
            pdfs = [f for f in os.listdir(folder) if f.endswith(".pdf")]

        if not pdfs:
            continue

        book_chunks = []
        pyq_chunks = []

        for pdf in pdfs:
            path = os.path.join(folder, pdf)
            try:
                loader = PyPDFLoader(path)
                pages = loader.load()
                splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
                chunks = splitter.split_documents(pages)

                for chunk in chunks:
                    chunk.metadata["subject"] = subject
                    fn = pdf.lower()
                    if fn.startswith("pyq_") or fn.startswith("bca") or "question" in fn:
                        chunk.metadata["type"] = "pyq"
                        pyq_chunks.append(chunk)
                    else:
                        chunk.metadata["type"] = "book"
                        book_chunks.append(chunk)
            except Exception as e:
                st.warning(f"⚠️ {pdf} load nahi hua: {e}")

        subject_dbs[subject] = {
            "book": FAISS.from_documents(book_chunks, embeddings) if book_chunks else None,
            "pyq": FAISS.from_documents(pyq_chunks, embeddings) if pyq_chunks else None,
            "book_count": len([p for p in pdfs if not p.startswith("pyq_") and not p.startswith("bca")]),
            "pyq_count": len([p for p in pdfs if p.startswith("pyq_") or p.startswith("bca")])
        }

    return subject_dbs

# ─── Subject Auto-Detect ──────────────────────────────────
def detect_subject(query, available_subjects, groq_client, lang):
    """LLM se detect karo — konsa subject hai question mein"""
    if len(available_subjects) == 1:
        return available_subjects[0]

    subjects_list = ", ".join(available_subjects)
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role": "user",
            "content": f"""Given these available subjects: {subjects_list}

Which subject does this question belong to? Reply with ONLY the subject name from the list, nothing else.
If unsure, reply with "general" or the closest match.

Question: {query}"""
        }],
        max_tokens=20
    )
    detected = response.choices[0].message.content.strip().lower().replace(" ", "_")

    # Match karo available subjects mein
    for s in available_subjects:
        if s in detected or detected in s:
            return s

    # Fallback — first subject
    return available_subjects[0]

# ─── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.2rem 1rem 0.8rem; border-bottom: 1px solid #1e1e1e; display:flex; align-items:center; gap:10px;">
        <div style="width:30px;height:30px;background:linear-gradient(135deg,rgb(255,75,75),rgb(255,140,0));border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;">🤖</div>
        <span style="font-size:0.88rem;font-weight:600;color:#e8e8e8;">GyanSathi AI</span>
        <span style="font-size:0.6rem;background:linear-gradient(135deg,rgb(255,75,75),rgb(255,140,0));color:#000;padding:2px 6px;border-radius:20px;font-weight:700;margin-left:auto;">BETA</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:0.7rem 0.8rem;border-bottom:1px solid #1a1a1a;">', unsafe_allow_html=True)
    if st.button("✏️  New Chat", key="new_chat_btn"):
        new_chat()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding:0.6rem 1rem 0.2rem;font-size:0.65rem;font-weight:600;color:#444;letter-spacing:1px;text-transform:uppercase;">Recent Chats</div>', unsafe_allow_html=True)

    for chat_id in reversed(list(st.session_state.all_chats.keys())):
        chat = st.session_state.all_chats[chat_id]
        is_active = chat_id == st.session_state.current_chat_id
        title = chat["title"]
        icon = "💬" if is_active else "🕐"
        style = "background:#1a1a1a;border:1px solid #2a2a2a;" if is_active else ""

        st.markdown(f'<div style="margin:0 0.5rem 2px;padding:0.45rem 0.6rem;border-radius:7px;{style}cursor:pointer;">', unsafe_allow_html=True)
        if st.button(f"{icon} {title}", key=f"chat_{chat_id}"):
            st.session_state.current_chat_id = chat_id
            st.session_state.quiz_active = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:auto;padding:0.8rem;border-top:1px solid #1a1a1a;position:absolute;bottom:0;width:calc(100% - 1.6rem);">', unsafe_allow_html=True)
    if st.button("🗑️  Clear Current Chat", key="clear_btn"):
        st.session_state.all_chats[st.session_state.current_chat_id]["messages"] = []
        st.session_state.all_chats[st.session_state.current_chat_id]["title"] = "New Chat"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Main Header ──────────────────────────────────────────
st.title("🤖 GyanSathi AI")
st.caption("Har Subject, Har Semester, Aapka Smart Saathi.")

col1, col2, col3 = st.columns([3, 2, 1])
with col2:
    selected_lang = st.selectbox("lang", options=list(LANGUAGES.keys()), index=0, label_visibility="collapsed")
with col3:
    quiz_mode = st.toggle("🧠 Quiz")
with col1:
    current_title = st.session_state.all_chats[st.session_state.current_chat_id]['title']
    st.caption(f"💬 {current_title[:30]}")

st.divider()

# ─── Load DBs ─────────────────────────────────────────────
with st.spinner("Loading knowledge base..."):
    subject_dbs = load_all_subject_dbs()

if not subject_dbs:
    st.warning("⚠️ Koi PDF nahi mili. Admin se upload karwao.")
    st.stop()

available_subjects = list(subject_dbs.keys())

# Stats dikhao
if not st.session_state.ready_msg_shown:
    subjects_info = " · ".join([
        f"**{s.replace('_',' ').title()}** ({subject_dbs[s]['book_count']}B/{subject_dbs[s]['pyq_count']}PYQ)"
        for s in available_subjects if s != "_general"
    ])
    msg = st.success(f"✅ Ready! {subjects_info}")
    time.sleep(2)
    msg.empty()
    st.session_state.ready_msg_shown = True

# Subject badges dikhao
badges = " ".join([f'<span class="subject-badge">{s.replace("_"," ").upper()}</span>'
                   for s in available_subjects if s != "_general"])
st.markdown(f"Available: {badges}", unsafe_allow_html=True)

st.divider()

# ─── Quick Actions ────────────────────────────────────────
if "English" in selected_lang:
    q1 = "Which questions are repeated across all question papers? List with answers."
    q2 = "Which topics are most important for exam?"
    q3 = "List all important topics that can come in exam."
elif "Hindi" in selected_lang:
    q1 = "Teeno papers mein konse questions repeat hue hain? List karo with answers."
    q2 = "Konse topics sabse zyada important hain exam ke liye?"
    q3 = "Saare important topics list karo."
else:
    q1 = "Konse questions papers mein repeat hue hain? List karo with answers."
    q2 = "Konse topics sabse zyada important hain exam ke liye?"
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

    # Pehle subject ka pyq_db use karo
    pyq_db = None
    for s in available_subjects:
        if subject_dbs[s]["pyq"]:
            pyq_db = subject_dbs[s]["pyq"]
            break

    if pyq_db:
        results = pyq_db.similarity_search("exam questions", k=4)
        context = "\n".join([r.page_content for r in results])
        client = Groq(api_key=st.secrets["GROQ_KEY"])
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"You are GyanSathi AI in Quiz Mode. {LANGUAGES[selected_lang]} Ask 1 MCQ from past exam questions. After answer, say correct/wrong, explain, then ask next."},
                {"role": "user", "content": f"Past exam questions:\n{context}\n\nAsk 1 MCQ."}
            ]
        )
        add_message("assistant", "🧠 **Quiz Mode ON!**\n\n" + response.choices[0].message.content)
elif not quiz_mode:
    st.session_state.quiz_active = False

# ─── Display Messages ─────────────────────────────────────
for msg in get_current_messages():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── Quick Query ──────────────────────────────────────────
query = None
if "quick_query" in st.session_state:
    query = st.session_state.quick_query
    del st.session_state.quick_query

user_input = st.chat_input("Ask anything — Cyber Security, E-Commerce, Java, Python...")
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
        subjects_list = ", ".join([s.replace("_", " ").title() for s in available_subjects if s != "_general"])
        answer = f"Main **GyanSathi AI** hun! 🤖 Main in subjects mein help kar sakta hun: **{subjects_list}**. Koi bhi topic poocho!"
        sources_text = ""
    else:
        client = Groq(api_key=st.secrets["GROQ_KEY"])

        # Auto-detect subject
        if len(available_subjects) > 1:
            detected_subject = detect_subject(query, available_subjects, client, selected_lang)
        else:
            detected_subject = available_subjects[0]

        # Us subject ka DB use karo
        db_info = subject_dbs.get(detected_subject, subject_dbs[available_subjects[0]])
        book_db = db_info["book"]
        pyq_db = db_info["pyq"]

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
        subject_display = detected_subject.replace("_", " ").title()

        if quiz_mode:
            system_content = f"You are GyanSathi AI in Quiz Mode. {lang_instruction} Check answer, say correct/wrong, explain briefly, then ask next MCQ."
            full_context = f"Past exam questions:\n{pyq_context}"
        elif is_repeat_query:
            system_content = f"""You are GyanSathi AI — Exam Expert for {subject_display}.
{lang_instruction}
Find repeated questions and list with answers.

FORMAT:
## 🔁 Repeat Questions
(⭐⭐⭐ = 3 papers, ⭐⭐ = 2 papers)
## 📖 Their Answers
## ⚠️ Exam Tip"""
            full_context = f"BOOK THEORY:\n{book_context}\n\nPAST EXAM PAPERS:\n{pyq_context}"
        else:
            system_content = f"""You are GyanSathi AI — {subject_display} mentor.
{lang_instruction}

FORMAT:
## 📖 Theory
## 📝 Previously Asked In Exam
## ⭐ Exam Tip

RULES: Focus on {subject_display} only. Ignore preface/dedication content."""
            full_context = f"BOOK THEORY:\n{book_context}\n\nPAST EXAM QUESTIONS:\n{pyq_context}"

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"Context:\n{full_context}\n\nQuestion: {query}"}
            ]
        )
        answer = response.choices[0].message.content

        # Subject badge answer ke saath
        answer = f'<span class="subject-badge">{subject_display}</span>\n\n' + answer

    with st.chat_message("assistant"):
        st.markdown(answer, unsafe_allow_html=True)
        if not is_identity and sources_text and not quiz_mode:
            with st.expander("📚 Sources"):
                st.caption(sources_text)

    full_answer = answer + (f"\n\nSources:\n{sources_text}" if sources_text and not quiz_mode else "")
    add_message("assistant", full_answer)