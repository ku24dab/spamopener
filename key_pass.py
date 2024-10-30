import streamlit as st

API_KEY = "당일 오픈 예정"

st.set_page_config(page_title="API Key", layout="centered")
st.title("🔑 API Key")

st.info("여러분들의 체험을 위해 10분간 api key 를 제공할 예정입니다.\n이후에는 여러분들의 gpt api key 로 이용하실 수 있습니다.")

if st.button("API 키 표시"):
    st.code(API_KEY, language="bash")