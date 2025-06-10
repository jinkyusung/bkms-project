import streamlit as st
import pandas as pd
import datetime as dt
from openai import OpenAI
from procedure import boot, purge, analyze_emotion, load_documents, build_vectorstore, analyze_emotion_and_confidence

# ------------------------------------------------------------------------------------------ #

args = boot()
client = OpenAI(api_key=args.openai_api_key)
text_csv = pd.read_csv(args.text_csv_path)
df_emotion = load_documents('./data/emotion_talks.csv', limit=1000)

st.set_page_config(page_title="나의 상담노트 감정 분석 챗봇", layout="centered")
st.title("🧠 나의 상담노트 감정 분석 챗봇")
st.write("감정일기를 입력하면 GPT가 핵심 감정을 분석해 드립니다.")

# ------------------------------------------------------------------------------------------ #

if "emotion_log" not in st.session_state:
    st.session_state.emotion_log = []

writen_date = st.date_input("**어느 날짜의 감정일기를 작성하시겠습니까?**", value=args.today, min_value=args.min_date, max_value=args.max_date)
text = st.text_area("✍️ 감정일기를 작성하세요", height=250)

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

if st.button("🔍 감정 분석하기"):
    if text.strip():
        with st.spinner("GPT가 감정을 분석하는 중입니다..."):
            vectorstore = build_vectorstore(df_emotion)
            result = analyze_emotion_and_confidence(text, vectorstore, top_k=5)
        try:
            major = result['major_emotion']
            minor = result['minor_emotion']
            confidence = result['confidence']

            st.session_state.emotion_log.append({
                "날짜": args.today,
                "감정 대분류": major,
                "감정 소분류": minor,
                "신뢰도": confidence
            })

            st.success(f"📌 감정 분석 결과: {major}-{minor} (신뢰도: {confidence:.2f})")
        except Exception as e:
            st.error(f"❌ 분석 결과 파싱 중 오류 발생: {e}")
    else:
        st.warning("먼저 감정일기를 입력해주세요!")

# if st.button("🔍 감정 분석하기"):
#     if text.strip():
#         with st.spinner("GPT가 감정을 분석하는 중입니다..."):
#             result = analyze_emotion(text)
#         try:
#             emotion_line = next(line for line in result.splitlines() if "감정" in line)
#             confidence_line = next(line for line in result.splitlines() if "신뢰도" in line)
#             emotion = emotion_line.split(":")[-1].strip()
#             confidence = float(confidence_line.split(":")[-1].strip())

#             st.session_state.emotion_log.append({
#                 "날짜": args.today,
#                 "감정": emotion,
#                 "신뢰도": confidence
#             })

#             st.success(f"📌 감정 분석 결과: {emotion} (신뢰도: {confidence:.2f})")
#         except Exception as e:
#             st.error(f"❌ 분석 결과 파싱 중 오류 발생: {e}")
#     else:
#         st.warning("먼저 감정일기를 입력해주세요!")

# 감정 추이 시각화
# if st.session_state.emotion_log:
#     st.markdown("---")
#     st.subheader("📈 감정 추이 그래프")

#     df = pd.DataFrame(st.session_state.emotion_log)
#     df_grouped = df.pivot_table(index="날짜", columns="감정", values="신뢰도", aggfunc="mean").fillna(0)
#     st.line_chart(df_grouped)

#     st.markdown("---")
#     st.subheader("📋 감정 분석 기록")
#     st.dataframe(df.sort_values(by="날짜", ascending=False))

# ------------------------------------------------------------------------------------------ #

purge()

# ------------------------------------------------------------------------------------------ #
