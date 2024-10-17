import streamlit as st
import openai
# from dotenv import load_dotenv
import os
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime
import yaml
import time
import sqlite3


# 유틸리티 함수들
def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# def get_spam_detection_reason(text):

#     return 

# 새로운 함수: 프롬프트 미리 로드
@st.cache_data

# def load_prompts():
#     prompt_path = 'prompt.txt'
#     prompt2_path = 'prompt2.txt'
    
#     prompt = load_txt(prompt_path)
#     prompt2 = load_txt(prompt2_path)
    
#     return prompt, prompt2

# # 수정된 pattern_recognition 함수
# def pattern_recognition(message_text, is_spam, temperature=0.0):
#     client = openai.OpenAI()
#     prompt, prompt2 = load_prompts()
    
#     messages = [
#         {"role": "system", "content": prompt},
#         {"role": "user", "content": message_text}
#     ]

#     response = client.chat.completions.create(
#         model='gpt-4o-2024-08-06',
#         messages=messages,
#         temperature=temperature
#     )

#     first_response = response.choices[0].message.content
#     messages.append({"role": "assistant", "content": first_response})
#     messages.append({"role": "user", "content" : prompt2 + is_spam})

#     response2 = client.chat.completions.create(
#         model='gpt-4o-2024-08-06',
#         messages=messages,
#         temperature=temperature
#     )
#     return response2.choices[0].message.content

def load_prompts():
    prompt_path = 'prompt.txt'
    prompt2_path = 'prompt2.txt'
    
    prompt = load_txt(prompt_path)
    prompt2 = load_txt(prompt2_path)
    
    return prompt, prompt2


def pattern_recognition(client, messages, temperature=0.0):
    response = client.chat.completions.create(
        model='gpt-4o-2024-08-06',
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

def spam_reasoning(client, messages, first_response, is_spam, temperature=0.0):
    _, prompt2 = load_prompts()
    messages.append({"role": "assistant", "content": first_response})
    messages.append({"role": "user", "content" : prompt2 + is_spam})

    response2 = client.chat.completions.create(
        model='gpt-4o-2024-08-06',
        messages=messages,
        temperature=temperature
    )
    return response2.choices[0].message.content


def get_external_data():
    conn = sqlite3.connect('/Users/kong/Library/Messages/chat.db')
    cursor = conn.cursor()
    cursor.execute("SELECT text, date FROM message ORDER BY date DESC LIMIT 1")
    messages = cursor.fetchall()
    conn.close()
    return messages


# def get_external_data():
#     return """국민연금 가입자 자격변동확인통지서
# [Web발신]
# ■ 제목 : 국민연금 가입자 자격변동확인통지서
# ■ 내용 : 국민연금 가입자 자격변동확인통지

# 상세내용은 아래의 링크를 통해 본인확인을 거쳐 세부 내용을 확인할 수 있습니다.

# 아래 버튼(주소) 클릭 시 접속 무료

# ■ 전자문서(안내문) 확인하기
# https://mpost.uplus.co.kr/read?c=20240829091628jjmUh

# ■ 국민연금 수신여부, 수신번호 지정
# https://mpost.uplus.co.kr/refuse?c=20240829091628jjmUh"""

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# 앱 초기화 및 설정
# load_dotenv()
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

# 사이드바 설정
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


# 메인 앱 함수
def main():
    # 제목과 이미지를 나란히 배치
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Spam Opener")
        st.write("")
        st.markdown("""
        ##### 스팸 메시지를 단순히 차단하는 것에 그치지 않고 그 메시지의 내부를 "열어" 구조와 내용을 분석하는 특성을 담고 있습니다. 
        ##### 이 프로그램은 스팸 메시지의 위험성을 세밀하게 해부하여 사용자에게 안전한 정보를 제공하는 "열쇠" 역할을 합니다.""") # 열쇠에서 대놓고 오프너로 바꾸는건 어땡?
        
    with col2:
        st.image("spam_opener.png", width=150)
    
    # 세션 상태 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
    # AI 분석 결과를 저장할 리스트를 초기화
    if 'results' not in st.session_state:
        st.session_state.results = []

    # 새로운 메시지가 추가되었는지를 추적하는 상태 변수 초기화
    if 'new_message_added' not in st.session_state:
        st.session_state.new_message_added = False

    if st.button("새로운 메시지 확인하기"):
        external_data = get_external_data()  # 최신 메시지 가져오기
        if external_data:
            # external_data는 리스트 안에 튜플 형태로 되어 있으므로, 첫 번째 튜플의 첫 번째 요소를 가져옵니다.
            message_text = external_data[0][0]  # 메시지 텍스트 추출
            st.session_state.messages.append({"role": "user", "content": message_text, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            st.session_state.new_message_added = True  # 메시지 추가됨을 추적

    # # 외부 데이터로 시작
    # if not st.session_state.messages:
    #     external_data = get_external_data()
    #     st.session_state.messages.append({"role": "user", "content": external_data, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

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

        # OpenAI API 키 설정
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    auth_path = yaml.safe_load(open('/Users/kong/Desktop/Codes/auth.yml', encoding='utf-8'))
    os.environ["OPENAI_API_KEY"] = auth_path['OpenAI']['key']

    # if not openai.api_key:
    #     # st.error("OpenAI API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 설정해주세요.")
    #     # st.stop()

    # 파일 경로 설정 및 텍스트 파일 로드
    spam_path = 'spam_text.txt'
    spam_text = load_txt(spam_path)

    client = openai.OpenAI()
    prompt, _ = load_prompts()
    messages_list = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": spam_text}
    ]
    first_response = pattern_recognition(client, messages_list)

    # 스팸 여부 확인 버튼
    if st.session_state.new_message_added:
    # if st.button('스팸 여부 확인'):
        last_message = st.session_state.messages[-1]['content']
        with st.spinner('AI가 메시지를 분석 중입니다...'):
            try:
                result = spam_reasoning(client, messages_list, first_response, last_message, temperature=0.0)
                #result = pattern_recognition(last_message, "Yes" if "스팸" in spam_text else "No")
                if result in "Danger":
                    st.error("Danger🚨 주의! AI 분석 결과, 이 메시지는 스팸일 가능성이 높습니다.")
                    st.write("Zero-Shot with Auto-Generated Prompt로 스팸을 탐지했습니다.")
                    split_result = result.split('1.')
                    if len(split_result) > 1:  # split 결과가 여러 부분으로 나뉘었을 때
                        reasoning_part = split_result[-1]  # 추론 부분을 선택
                    else:
                        reasoning_part = result  # split되지 않은 경우 전체 결과 사용

                    st.write('1.',reasoning_part)
                elif result in "Warning":
                    st.warning("Warning⚠️ AI 분석 결과, 이 메시지는 스팸일 가능성이 있습니다.")
                    st.write("Zero-Shot with Auto-Generated Prompt로 스팸을 탐지했습니다.")
                    split_result = result.split('1.')
                    if len(split_result) > 1:  # split 결과가 여러 부분으로 나뉘었을 때
                        reasoning_part = split_result[-1]  # 추론 부분을 선택
                    else:
                        reasoning_part = result  # split되지 않은 경우 전체 결과 사용

                    st.write('1.',reasoning_part)

                elif result in "Safe":
                    st.success("Safe✅ AI 분석 결과, 이 메시지는 정상으로 보입니다.")
                
            # # 결과 분석
            # if "danger" in result.lower():
            #     analysis = "Danger🚨 주의! AI 분석 결과, 이 메시지는 스팸일 가능성이 높습니다."
            #     analysis_class = "danger"
            # elif "warning" in result.lower():
            #     analysis = "Warning⚠️ AI 분석 결과, 이 메시지는 스팸일 가능성이 있습니다."
            #     analysis_class = "warning"
            # else:
            #     analysis = "Safe✅ AI 분석 결과, 이 메시지는 정상으로 보입니다."
            #     analysis_class = "safe"
            
            # # AI 응답 추가
            # ai_response = {
            #     "role": "assistant", 
            #     "content": result, 
            #     "analysis": analysis,
            #     "analysis_class": analysis_class,
            #     "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # }
            # st.session_state.messages.append(ai_response)
            
            # # 상세 정보 (스팸으로 판단될 때만)
            # if analysis_class in ["danger", "warning"]:
            #     with st.expander("상세 정보 보기"):
            #         st.subheader("스팸 탐지 이유")
            #         reason = get_spam_detection_reason(result)
            #         st.write(reason)
            
            # st.experimental_rerun()
            
            except Exception as e:
                st.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")
        # 과거 분석 결과 출력
    if st.session_state.results:
        st.subheader("이전 분석 결과")
        for entry in st.session_state.results:
            st.markdown(f"**메시지**: {entry['message']}")
            st.markdown(f"**분석 결과**: {entry['result']}")
            st.markdown("---")

if __name__ == "__main__":
    main()