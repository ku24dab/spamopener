import streamlit as st
import openai
import os
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime
import sqlite3

# 파일 경로 상수 정의
PATHS = {
    'prompt': 'prompt.txt',
    'prompt2': 'prompt2.txt',
    'db': 'messages.db',  # 현재 폴더에 DB 생성
    'spam_icon': 'spam_opener.png',
    'model': 'gpt-4o-2024-08-06',
}

def init_db():
    conn = sqlite3.connect(PATHS['db'])
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS message (
        text TEXT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

@st.cache_data
def load_prompts():
    prompt = load_txt(PATHS['prompt'])
    prompt2 = load_txt(PATHS['prompt2'])
    return prompt, prompt2

def pattern_recognition(client, messages, temperature=0.0):
    response = client.chat.completions.create(
        model=PATHS['model'],
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

def spam_reasoning(client, messages, first_response, is_spam, temperature=0.0):
    _, prompt2 = load_prompts()
    messages.append({"role": "assistant", "content": first_response})
    messages.append({"role": "user", "content": prompt2 + is_spam})

    response2 = client.chat.completions.create(
        model=PATHS['model'],
        messages=messages,
        temperature=temperature
    )
    return response2.choices[0].message.content

def get_external_data():
    conn = sqlite3.connect(PATHS['db'])
    cursor = conn.cursor()
    cursor.execute("SELECT text, date FROM message ORDER BY date DESC LIMIT 1")
    messages = cursor.fetchall()
    conn.close()
    return messages

def add_message_to_db(message_text):
    conn = sqlite3.connect(PATHS['db'])
    cursor = conn.cursor()
    cursor.execute("INSERT INTO message (text) VALUES (?)", (message_text,))
    conn.commit()
    conn.close()

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

st.set_page_config(page_title="Spam Opener", page_icon="🥫", layout="wide")

# CSS 스타일 정의
st.markdown("""
<style>
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .message {
        max-width: 70%;
        padding: 10px;
        border-radius: 20px;
    }
    .user-message {
        align-self: flex-end;
        background-color: #FFE2DD;
    }
    .ai-message {
        align-self: flex-start;
        background-color: #ffffff;
    }
    .timestamp {
        font-size: 0.8em;
        color: #888;
        margin-top: 5px;
    }
    .analysis-result {
        margin-top: 5px;
        padding: 5px;
        border-radius: 5px;
    }
    .danger {
        background-color: #ffcccc;
    }
    .warning {
        background-color: #fff4cc;
    }
    .safe {
        background-color: #F8F8F8;
    }
</style>
""", unsafe_allow_html=True)

def main():
    init_db()
        
    # 사이드바 설정
       # 사이드바에 DT Day 이미지 추가 
    st.sidebar.image("KUBS_DT_LOGO.png", width=300)  # 이미지 크기 조정
    
        # API 키 설정
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    
    api_key = st.sidebar.text_input("OpenAI API Key", 
                                   value=st.session_state.api_key,
                                   type="password")
    if api_key:
        st.session_state.api_key = api_key

    
    st.sidebar.header("사용 방법")
    st.sidebar.write("""
    1. 외부에서 실시간으로 받은 메시지가
    자동으로 표시됩니다.
    2. '스팸 여부 확인' 버튼을 클릭하여
    AI 분석을 시작하세요.
    3. AI의 분석 결과를 확인하세요!
    """)

    st.sidebar.info('''
    이 앱은 Zero-Shot with Auto-Generated Prompt를 기반으로 개발되었습니다.
    ''')

    # 학교 로고 및 카피라이트
    school_logo = Image.open("korea_univ.png")
    school_logo_base64 = image_to_base64(school_logo)

    st.sidebar.markdown(f"""
        <div style="text-align: center; margin-top: 50px;">
            <img src="data:image/png;base64,{school_logo_base64}" width="200"/>
            <p>© 2024 Openers 이자경&김은채<br>All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)

    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.results = []
        st.session_state.new_message_added = False

    # UI Layout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Spam Opener")
        st.write("")
        st.markdown("""
        ##### 스팸 메시지를 단순히 차단하는 것에 그치지 않고 그 메시지의 내부를 "열어" 구조와 내용을 분석하는 특성을 담고 있습니다. 
        ##### 이 프로그램은 스팸 메시지의 위험성을 세밀하게 해부하여 사용자에게 안전한 정보를 제공하는 "오프너" 역할을 합니다.""")
    
    with col2:
        st.image("spam_opener.png", width=150)

    # 수동 메시지 입력
    manual_message = st.text_area("수기로 메시지 입력", height=100)
    if st.button("수기 메시지 분석하기") and manual_message:
        add_message_to_db(manual_message)
        st.session_state.messages.append({
            "role": "user",
            "content": manual_message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.session_state.new_message_added = True
    
    # iMessage에서 메시지 가져오기
    if st.button("새로운 메시지 확인하기"):
        external_data = get_external_data()
        if external_data:
            message_text = external_data[0][0]
            st.session_state.messages.append({
                "role": "user",
                "content": message_text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.session_state.new_message_added = True

    # 채팅 창
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="message user-message">{message["content"]}<div class="timestamp">{message["timestamp"]}</div></div>', unsafe_allow_html=True)
            else:
                analysis_class = message.get("analysis_class", "safe")
                st.markdown(f'''
                <div class="message ai-message">
                    {message["content"]}
                    <div class="timestamp">{message["timestamp"]}</div>
                    <div class="analysis-result {analysis_class}">{message.get("analysis", "")}</div>
                </div>
                ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 분석 로직
    if st.session_state.api_key:
        try:
            client = openai.OpenAI(api_key=st.session_state.api_key)
            prompt, _ = load_prompts()
            spam_text = load_txt('spam_text.txt')
            messages_list = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": spam_text}
            ]
            
            if st.session_state.new_message_added:
                first_response = pattern_recognition(client, messages_list)
                last_message = st.session_state.messages[-1]['content']
                
                with st.spinner('AI가 메시지를 분석 중입니다...'):
                    result = spam_reasoning(client, messages_list, first_response, last_message)
                    st.session_state.results.append({
                        "message": last_message,
                        "result": result
                    })

                    if "Danger" in result:
                        st.error("Danger🚨 주의! AI 분석 결과, 이 메시지는 스팸일 가능성이 높습니다.")
                        split_result = result.split('1.')
                        reasoning_part = split_result[-1] if len(split_result) > 1 else result
                        st.write('1.', reasoning_part)
                    elif "Warning" in result:
                        st.warning("Warning⚠️ AI 분석 결과, 이 메시지는 스팸일 가능성이 있습니다.")
                        split_result = result.split('1.')
                        reasoning_part = split_result[-1] if len(split_result) > 1 else result
                        st.write('1.', reasoning_part)
                    elif "Safe" in result:
                        st.success("Safe✅ AI 분석 결과, 이 메시지는 정상으로 보입니다.")

                st.session_state.new_message_added = False

        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
    else:
        st.warning("OpenAI API 키를 입력해주세요.")

    if st.session_state.results:
        st.subheader("분석 결과")
        for idx, entry in enumerate(st.session_state.results):
            with st.expander(f"메시지 {idx + 1}"):
                st.markdown(f"**메시지 내용**: {entry['message']}")
                st.markdown(f"**분석 결과**: {entry['result']}")

if __name__ == "__main__":
    main()