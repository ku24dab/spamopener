import streamlit as st
import pyperclip

API_KEY = "여기에_API_키를_입력하세요"  # 이 부분에 실제 API 키를 넣으세요

st.set_page_config(page_title="API Key", layout="centered")
st.title("🔑 API Key")

if st.button("API 키 복사"):
    pyperclip.copy(API_KEY)
    st.success("API 키가 클립보드에 복사되었습니다!")
    st.code(API_KEY)
