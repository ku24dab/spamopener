import streamlit as st

API_KEY = "여기에_API_키를_입력하세요"

st.set_page_config(page_title="API Key", layout="centered")
st.title("🔑 API Key")

if st.button("API 키 표시"):
    st.code(API_KEY, language="bash")