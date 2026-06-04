import streamlit as st
import os

st.set_page_config(
    page_title="Admin Panel", 
    page_icon="🔒",
    initial_sidebar_state="auto"
    
    )

# Simple password protection
PASSWORD = "admin123"

st.title("🔒 Admin Panel")

pwd = st.text_input("Password enter karo:", type="password")

if pwd != PASSWORD:
    st.warning("Password daalo access ke liye.")
    st.stop()

st.success("✅ Access mil gaya!")
st.subheader("📤 PDF Upload Karo")

PDF_FOLDER = "pdfs"

uploaded = st.file_uploader(
    "PDF select karo",
    accept_multiple_files=True,
    type="pdf"
)

if uploaded:
    for file in uploaded:
        save_path = os.path.join(PDF_FOLDER, file.name)
        with open(save_path, "wb") as f:
            f.write(file.read())
        st.success(f"✅ {file.name} save ho gaya!")

    st.info("⚠️ Chat page reload karo nayi PDFs ke liye.")

# Saved PDFs list
st.subheader("📁 Saved PDFs")
files = os.listdir(PDF_FOLDER)
if files:
    for f in files:
        col1, col2 = st.columns([3, 1])
        col1.write(f"📄 {f}")
        if col2.button("🗑️ Delete", key=f):
            os.remove(os.path.join(PDF_FOLDER, f))
            st.rerun()
else:
    st.write("Koi PDF nahi hai abhi.")