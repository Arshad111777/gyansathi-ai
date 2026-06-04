import streamlit as st
import os
import shutil

st.set_page_config(
    page_title="Admin Panel",
    page_icon="🔒",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');
* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f0f0f !important;
    color: #e8e8e8 !important;
    font-family: 'Sora', sans-serif !important;
}
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
.main .block-container { max-width: 800px !important; margin: 0 auto !important; padding: 2rem 1.5rem !important; }
[data-testid="stAppViewContainer"] > .main { background: #0f0f0f !important; }
.stButton > button {
    background: #1a1a1a !important; color: #ccc !important;
    border: 1px solid #2a2a2a !important; border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important; transition: all 0.2s !important;
}
.stButton > button:hover { background: #222 !important; color: #fff !important; border-color: #333 !important; }
[data-testid="stTextInput"] input {
    background: #141414 !important; border: 1px solid #222 !important;
    border-radius: 8px !important; color: #e8e8e8 !important; font-family: 'Sora', sans-serif !important;
}
[data-testid="stAlert"] { background: #141414 !important; border: 1px solid #222 !important; border-radius: 8px !important; }
[data-testid="stExpander"] { background: #141414 !important; border: 1px solid #1e1e1e !important; border-radius: 8px !important; }
hr { border: none !important; border-top: 1px solid #1e1e1e !important; margin: 1rem 0 !important; }
.subject-card {
    background: #141414; border: 1px solid #1e1e1e; border-radius: 10px;
    padding: 1rem 1.2rem; margin-bottom: 0.6rem;
}
.subject-card h4 { color: #e8e8e8; font-size: 0.9rem; margin-bottom: 0.3rem; }
.subject-card p { color: #666; font-size: 0.75rem; }
.subject-tag {
    display: inline-block; background: #1e1e1e; color: #aaa;
    padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; margin-right: 4px;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

PASSWORD = "admin123"
PDF_FOLDER = "pdfs"

# Ensure base folder exists
os.makedirs(PDF_FOLDER, exist_ok=True)

st.title("🔒 Admin Panel")
st.caption("GyanSathi AI — Content Management")

pwd = st.text_input("Password:", type="password", placeholder="Enter admin password")
if pwd != PASSWORD:
    st.warning("Password daalo access ke liye.")
    st.stop()

st.success("✅ Access granted!")
st.divider()

# ─── Upload Section ───────────────────────────────────────
st.subheader("📤 PDF Upload")

col1, col2 = st.columns([2, 1])

with col1:
    subject_name = st.text_input(
        "Subject Name",
        placeholder="e.g. cyber_security, java, python, ecommerce",
        help="Lowercase, underscore se words join karo. e.g. 'data_structures'"
    )

with col2:
    pdf_type = st.selectbox(
        "PDF Type",
        options=["book", "pyq"],
        format_func=lambda x: "📚 Book/Notes" if x == "book" else "📝 Question Paper (PYQ)"
    )

uploaded = st.file_uploader(
    "PDF files select karo",
    accept_multiple_files=True,
    type="pdf"
)

if st.button("⬆️ Upload PDFs", disabled=not (subject_name and uploaded)):
    if not subject_name:
        st.error("Subject name daalo pehle!")
    elif not uploaded:
        st.error("Koi file select nahi ki!")
    else:
        # Clean subject name
        clean_subject = subject_name.strip().lower().replace(" ", "_")
        subject_folder = os.path.join(PDF_FOLDER, clean_subject)
        os.makedirs(subject_folder, exist_ok=True)

        for file in uploaded:
            # PYQ ko prefix lagao taaki identify ho sake
            if pdf_type == "pyq":
                filename = f"pyq_{file.name}" if not file.name.startswith("pyq_") else file.name
            else:
                filename = file.name

            save_path = os.path.join(subject_folder, filename)
            with open(save_path, "wb") as f:
                f.write(file.read())
            st.success(f"✅ `{filename}` → `pdfs/{clean_subject}/`")

        st.info("⚠️ Home page pe 'Clear Cache' karke reload karo nayi PDFs ke liye.")

st.divider()

# ─── Subjects Overview ────────────────────────────────────
st.subheader("📁 Subjects & PDFs")

# Get all subject folders
subjects = [d for d in os.listdir(PDF_FOLDER)
            if os.path.isdir(os.path.join(PDF_FOLDER, d))]

# Also check root PDFs (old style)
root_pdfs = [f for f in os.listdir(PDF_FOLDER)
             if f.endswith(".pdf")]

if root_pdfs:
    st.warning(f"⚠️ {len(root_pdfs)} PDFs root folder mein hain — inhe subject folders mein move karo!")
    with st.expander("📂 Root PDFs dekho"):
        for f in root_pdfs:
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.caption(f"📄 {f}")
            move_to = col2.text_input("Move to subject:", key=f"move_{f}", placeholder="subject_name")
            if col3.button("Move", key=f"movebtn_{f}"):
                if move_to:
                    dest = os.path.join(PDF_FOLDER, move_to.lower().replace(" ", "_"))
                    os.makedirs(dest, exist_ok=True)
                    shutil.move(os.path.join(PDF_FOLDER, f), os.path.join(dest, f))
                    st.success(f"Moved!")
                    st.rerun()

if not subjects:
    st.info("Koi subject folder nahi hai abhi. Upar se PDF upload karo!")
else:
    for subject in sorted(subjects):
        subject_path = os.path.join(PDF_FOLDER, subject)
        all_files = [f for f in os.listdir(subject_path) if f.endswith(".pdf")]
        books = [f for f in all_files if not f.startswith("pyq_")]
        pyqs = [f for f in all_files if f.startswith("pyq_")]

        with st.expander(f"📚 {subject.replace('_', ' ').title()} ({len(all_files)} files)"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**📖 Books ({len(books)})**")
                for f in books:
                    c1, c2 = st.columns([4, 1])
                    c1.caption(f"📄 {f}")
                    if c2.button("🗑", key=f"del_{subject}_{f}"):
                        os.remove(os.path.join(subject_path, f))
                        st.rerun()

            with col2:
                st.markdown(f"**📝 PYQs ({len(pyqs)})**")
                for f in pyqs:
                    c1, c2 = st.columns([4, 1])
                    c1.caption(f"📄 {f}")
                    if c2.button("🗑", key=f"del_{subject}_{f}"):
                        os.remove(os.path.join(subject_path, f))
                        st.rerun()

            # Delete subject folder
            if len(all_files) == 0:
                if st.button(f"🗑️ Delete '{subject}' folder", key=f"delfolder_{subject}"):
                    shutil.rmtree(subject_path)
                    st.rerun()

st.divider()
st.caption("💡 Tip: Subject name consistent rakho — e.g. 'cyber_security' hamesha same likho")