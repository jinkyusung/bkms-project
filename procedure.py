from dataclasses import dataclass
import datetime as dt
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import os
import streamlit as st
from pandas import DataFrame
import shutil
import pathlib
import json

# ------------------------------------------------------------------------------------------ #


@dataclass
class Arguments:
    """
    Arguments class to hold the configuration for the application.
    """
    openai_api_key: str

    today: datetime
    min_date: datetime
    max_date: datetime
    
    text_csv_path: DataFrame


# ------------------------------------------------------------------------------------------ #


def boot() -> Arguments:
    """
    Args:
        None
    Returns:
        args: An instance of Arguments containing the OpenAI API key and other configurations.
    """
    # Load OpenAI API key from environment variables.
    if not os.path.exists("./.env"):
        st.stop()
        raise FileNotFoundError("환경변수 파일 `.env`가 존재하지 않습니다. 이 파일을 생성하고 `OPENAI_API_KEY`를 설정해주세요.")
    load_dotenv()
    open_api_key = os.getenv('OPENAI_API_KEY')
    
    if not open_api_key:
        st.stop()
        raise ValueError("환경변수 `OPENAI_API_KEY`가 설정되지 않았습니다. 이 값을 `.env` 파일에 추가해주세요.")
    
    # Set up the dates.
    today = dt.date.today()
    min_date = today - dt.timedelta(days=180)
    max_date = today + dt.timedelta(days=7)

    # Set up the CSV path.
    text_csv_path = os.getenv('TEXT_CSV_PATH')

    csv_dir = os.path.dirname(text_csv_path)
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir, exist_ok=True)

    if not os.path.exists(text_csv_path):
        text_csv = pd.DataFrame(columns=["text", "date", "timestamp"])
        text_csv.to_csv(text_csv_path, index=False)

    # Create an instance of Arguments with the loaded configurations.
    args = Arguments(
        openai_api_key=open_api_key,
        today=today,
        min_date=min_date,
        max_date=max_date, 
        text_csv_path=text_csv_path
    )

    return args

def purge() -> None:
    # Remove all __pycache__ directories.
    for pycache in pathlib.Path(".").rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)
            print(f"[PURGE] Remove unusable files: {pycache}")


# ------------------------------------------------------------------------------------------ #


def analyze_emotion(client, text):
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

# ------------------------------------------------------------------------------------------ #

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate

def load_documents(csv_path: str, limit: int = 100) -> list:
    df = pd.read_csv(csv_path).dropna(subset=["human_speech"]).head(limit)
    documents = [
        Document(
            page_content=row["human_speech"],
            metadata={
                "major_emotion": row.get("major_emotion", ""),
                "minor_emotion": row.get("minor_emotion", "")
            }
        )
        for _, row in df.iterrows()
    ]
    return documents

def build_vectorstore(documents: list) -> FAISS:
    embedding_model = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embedding_model)
    return vectorstore

def analyze_emotion_and_confidence(user_input: str, vectorstore: FAISS, top_k: int = 5) -> dict:
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
    relevant_docs = retriever.get_relevant_documents(user_input)

    context = "\n".join([doc.page_content for doc in relevant_docs])

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    prompt_template = PromptTemplate.from_template("""
    다음은 사용자가 작성한 감정 표현입니다:
    "{user_input}"

    아래는 데이터셋에서 검색된 유사 문장들입니다:
    ---
    {context}
    ---

    위 정보를 참고하여 사용자의 감정을 다음 JSON 형식으로 분석해 주세요:
    {{
        "major_emotion": "<기쁨, 슬픔, 분노, 불안, 당황, 상처, 중립 중 하나>",
        "minor_emotion": "<보다 구체적인 감정 소분류>",
        "confidence": <0.0 ~ 1.0 사이의 신뢰도 숫자>
    }}
    반드시 JSON 형태로만 출력해 주세요.
    """)

    prompt = prompt_template.format(user_input=user_input, context=context)
    response = llm.predict(prompt)

    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        parsed = {"error": "Invalid JSON returned from GPT", "raw": response}

    return parsed
