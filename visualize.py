import streamlit as st
import pandas as pd
import plotly.express as px


# ------------------------------------------------------------------------------------------ #


emotion_colors = {
    "분노": "#FFADAD",
    "불안": "#FFD6A5",
    "당황": "#FDFFB6",
    "슬픔": "#A0C4FF",
    "상처": "#BDB2FF",
    "기쁨": "#CAFFBF",
    "중립": "#EDEDE9",
}


# ------------------------------------------------------------------------------------------ #


def calendar(emotion_data):
    end_date = pd.to_datetime("today").normalize()
    start_date = end_date - pd.Timedelta(days=29)
    date_range = pd.date_range(start=start_date, end=end_date)

    emotion_data_30 = emotion_data[(emotion_data['date'] >= start_date) & (emotion_data['date'] <= end_date)]

    # 날짜별 주요 감정 매핑
    emotion_by_day = {
        date.date(): group['major_emotion'].value_counts().idxmax()
        for date, group in emotion_data_30.groupby('date')
    }

    st.markdown(f"### 최근 30일 감정 캘린더 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})")

    calendar_html = "<table style='width:100%; text-align:center;'>"
    calendar_html += "<tr>" + "".join(f"<th>{day}</th>" for day in ["월", "화", "수", "목", "금", "토", "일"]) + "</tr><tr>"

    padding = (start_date.weekday()) % 7
    calendar_html += "<td></td>" * padding

    for i, day in enumerate(date_range):
        emotion = emotion_by_day.get(day.date(), "없음")
        color = emotion_colors.get(emotion, "#FFFFFC")
        calendar_html += f"<td style='background-color:{color}; padding:10px; border-radius:5px;'>{day.day}<br><small>{emotion}</small></td>"

        if (i + padding + 1) % 7 == 0:
            calendar_html += "</tr><tr>"

    calendar_html += "</tr></table>"
    st.markdown(calendar_html, unsafe_allow_html=True)
    

# ------------------------------------------------------------------------------------------ #


def pie_chart(df):
    today = pd.to_datetime("today").normalize()
    last_7_days = df[df['date'] >= (today - pd.Timedelta(days=7))]
    last_30_days = df[df['date'] >= (today - pd.Timedelta(days=30))]

    valid_7 = last_7_days[last_7_days["major_emotion"].notna()]
    valid_30 = last_30_days[last_30_days["major_emotion"].notna()]

    col1, col2 = st.columns(2)

    with col1:
        fig7 = px.pie(
            valid_7,
            names="major_emotion",
            title="최근 7일 감정 분포",
            color="major_emotion",
            color_discrete_map=emotion_colors
        )
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        fig30 = px.pie(
            valid_30,
            names="major_emotion",
            title="최근 30일 감정 분포",
            color="major_emotion",
            color_discrete_map=emotion_colors
        )
        st.plotly_chart(fig30, use_container_width=True)