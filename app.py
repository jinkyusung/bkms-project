# app.py
import streamlit as st
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from openai import OpenAI

from dotenv import load_dotenv


# .env 파일에서 환경 변수 로드
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    error_msg = """OpenAI API 키가 설정되지 않았습니다. 환경변수 파일 `.env`를 만들고 `OPENAI_API_KEY`를 설정해주세요."""
    st.stop()

client = OpenAI(api_key=openai_api_key)


if "emotion_log" not in st.session_state:
    st.session_state.emotion_log = []

# 앱 UI 설정
st.set_page_config(page_title="나의 상담노트 감정 분석 챗봇", layout="centered")
st.title("🧠 나의 상담노트 감정 분석 챗봇")
st.write("감정일기를 입력하면 GPT가 핵심 감정을 분석해 드립니다.")

# 감정일기 입력
user_input = st.text_area("✍️ 감정일기를 작성하세요", height=250)

# GPT 감정 분석 함수
def analyze_emotion(text):
    prompt = f"""
    다음은 한 사용자의 감정일기입니다. 이 일기의 핵심 감정 하나를 정해주고, 신뢰도를 0~1 사이 수치로 제시해줘. 예시는 다음과 같아:
    감정: 슬픔\n신뢰도: 0.83

    일기: {text}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 감정 분석 전문가야."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# 분석 버튼 동작
if st.button("🔍 감정 분석하기"):
    if user_input.strip():
        with st.spinner("GPT가 감정을 분석하는 중입니다..."):
            result = analyze_emotion(user_input)

        try:
            emotion_line = next(line for line in result.splitlines() if "감정" in line)
            confidence_line = next(line for line in result.splitlines() if "신뢰도" in line)
            emotion = emotion_line.split(":")[-1].strip()
            confidence = float(confidence_line.split(":")[-1].strip())

            today = datetime.now().strftime("%Y-%m-%d")
            st.session_state.emotion_log.append({
                "날짜": today,
                "감정": emotion,
                "신뢰도": confidence
            })

            st.success(f"📌 감정 분석 결과: {emotion} (신뢰도: {confidence:.2f})")
        except Exception as e:
            st.error(f"❌ 분석 결과 파싱 중 오류 발생: {e}")
    else:
        st.warning("먼저 감정일기를 입력해주세요!")

# 감정 추이 시각화
if st.session_state.emotion_log:
    st.markdown("---")
    st.subheader("📈 감정 추이 그래프")

    df = pd.DataFrame(st.session_state.emotion_log)
    df_grouped = df.pivot_table(index="날짜", columns="감정", values="신뢰도", aggfunc="mean").fillna(0)
    st.line_chart(df_grouped)

    st.markdown("---")
    st.subheader("📋 감정 분석 기록")
    st.dataframe(df.sort_values(by="날짜", ascending=False))
