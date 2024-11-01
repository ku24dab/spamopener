import streamlit as st

API_KEY = "sk-0L8MBDvJOTDkYAEwzQA36icYRXmiZb8KnPXRIWxaO9T3BlbkFJfJdvMPs95O2gF1CmHMveipJiHi5-Y1jh89ZkBbQRY"

st.set_page_config(page_title="API Key", layout="centered")
st.title("🔑 API Key")


st.info("여러분들의 체험을 위해 10분간 api key 를 제공할 예정입니다.\n이후에는 여러분들의 openai api key로 이용하실 수 있습니다. \n보안을 위해 마지막 api key 를 삭제하였습니다. 마지막 단어 A를 추가해주세요")

if st.button("API 키 표시"):
    st.code(API_KEY, language="bash")
