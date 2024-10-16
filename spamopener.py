import yaml
import openai
import os

# 1. 텍스트 파일 불러오기 (스팸 문자, 프롬프트, 프롬프트2)
def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

spam_path='spam_text.txt'
prompt_path='prompt.txt'
prompt2_path='prompt2.txt'

spam_text = load_txt(spam_path)
prompt = load_txt(prompt_path)
promt2 = load_txt(prompt2_path)


# API Key 설정하기
auth_path = yaml.safe_load(open('/Users/kong/Desktop/Codes/auth_personal.yml', encoding='utf-8'))
os.environ["OPENAI_API_KEY"] = auth_path['OpenAI']['key']

client = openai.OpenAI()


# 대망의 SpamOpenner
def pattern_recognition(prompt, prompt2, message_text, is_spam, temperature=0.0):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": message_text}
    ]

    response = client.chat.completions.create(
        model='gpt-4o-2024-08-06',
        messages=messages,
        temperature=temperature
    )

    first_response = response.choices[0].message.content
    messages.append({"role": "assistant", "content": first_response})
    messages.append({"role": "user", "content" : prompt2 + is_spam})

    response2 = client.chat.completions.create(
        model='gpt-4o-2024-08-06',
        messages=messages,
        temperature=temperature
    )
    return response2
