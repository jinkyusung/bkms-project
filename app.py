import streamlit as st
import pandas as pd
import datetime as dt
from openai import OpenAI
from procedure import boot, purge, analyze_emotion, load_documents, build_vectorstore, analyze_emotion_and_confidence
import streamlit as st
import plotly.express as px
import visualize

# ------------------------------------------------------------------------------------------ #

args = boot()
client = OpenAI(api_key=args.openai_api_key)
text_csv = pd.read_csv(args.text_csv_path)
emotion_csv = pd.read_csv(args.emotion_csv_path)
df_emotion = load_documents('./data/emotion_talks.csv', limit=1000)

st.set_page_config(page_title="나의 상담노트 감정 분석 챗봇", layout="centered")
st.title("🧠 나의 상담노트 감정 분석 챗봇")
st.write("감정일기를 입력하면 GPT가 핵심 감정을 분석해 드립니다.")

@st.cache_data
def load_emotion_history():
    emotion_history = pd.read_csv(args.emotion_csv_path, parse_dates=["date", "timestamp"])
    return emotion_history

emotion_history = load_emotion_history()

# ------------------------------------------------------------------------------------------ #

writen_date = st.date_input("**어느 날짜의 감정일기를 작성하시겠습니까?**", value=args.today, min_value=args.min_date, max_value=args.max_date)
text = st.text_area("✍️ 감정일기를 작성하세요", height=250)

# ------------------------------------------------------------------------------------------ #

if st.button("📝 감정일기 저장하기"):  # for develope (without api call)
    if text.strip():
        try:
            timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([{"text": text, "date": writen_date, "timestamp": timestamp}])
            text_csv = pd.concat([text_csv, new_row], ignore_index=True)
            text_csv.to_csv(args.text_csv_path, index=False)
            st.success(f"일기 저장 성공")

        except Exception as e:
            timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ------------------------------------------------------------------------------------------ #

if st.button("🔍 감정 분석하기"):
    if text.strip():
        with st.spinner("GPT가 감정을 분석하는 중입니다..."):
            vectorstore = build_vectorstore(df_emotion)
            result = analyze_emotion_and_confidence(text, vectorstore, top_k=5)
        try:
            major = result['major_emotion']
            minor = result['minor_emotion']
            confidence = result['confidence']

            st.success(f"📌 감정 분석 결과: {major}-{minor} (신뢰도: {confidence:.2f})")

            timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([{"major_emotion": major, "minor_emotion": minor, "confidence":confidence, "date": writen_date, "timestamp": timestamp}])
            emotion_csv = pd.concat([emotion_csv, new_row], ignore_index=True)
            emotion_csv.to_csv(args.emotion_csv_path, index=False)
            st.success(f"분석 결과 저장 성공")

            emotion_history = load_emotion_history()

            new_row = pd.DataFrame([{"text": text, "date": writen_date, "timestamp": timestamp}])
            text_csv = pd.concat([text_csv, new_row], ignore_index=True)
            text_csv.to_csv(args.text_csv_path, index=False)
            st.success(f"일기 저장 성공")

        except Exception as e:
            st.error(f"❌ 분석 결과 파싱 중 오류 발생: {e}")
    else:
        st.warning("먼저 감정일기를 입력해주세요!")

# ------------------------------------------------------------------------------------------ #

if not emotion_history.empty:
    st.subheader("📊 최근 감정 분포 (파이 차트)")
    visualize.pie_chart(emotion_history)

    st.subheader("📅 감정 일기 (캘린더 뷰)")
    visualize.calendar(emotion_history)

# ------------------------------------------------------------------------------------------ #

purge()
