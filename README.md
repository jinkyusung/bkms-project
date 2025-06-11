# 감정분석 챗봇

## I. Structure

### 1. Directory

```bash
project-root/
├── data/
│   ├── emotion_talks.csv
│   ├── emotion.csv  # 감정 분석 기록 저장
│   ├── text.csv  # 일기 raw text 저장
│   ├── 감성대화말뭉치(최종데이터)_Training.xlsx
│   └── 감성대화말뭉치(최종데이터)_Validation.xlsx
├── .env
├── .gitignore
├── README.md
├── app.py
├── preprocess.py
├── procedure.py
└── requirements.txt
```

### 2. Prepare Data for RAG

<!-- 이는 General한 실행 방법입니다만, 채점의 편의를 위해서 조교님께 드리는 파일에는 data 폴더 및 예시데이터를 포함하였으니 이 과정은 무시하셔도 됩니다! -->

1. AI허브에서 감성 대화 말뭉치 데이터를 [다운로드](https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=86)한다.  

2. 다운로드한 디렉토리 `18.감성대화` 에서 다음 두 가지 `zip` 파일을 압축 해제하여 `xlsx` 파일을 얻는다.  
    - `Training_221115_add/원천데이터/감성대화말뭉치(최종데이터)_Training.zip` ❯❯❯ `감성대화말뭉치(최종데이터)_Training.xlsx`
    - `Validation_221115_add/원천데이터/감성대화말뭉치(최종데이터)_Validation.zip` ❯❯❯ `감성대화말뭉치(최종데이터)_Validation.xlsx`

3. `xlsx` 파일을 `data` 디렉토리에 넣는다.  

4. **`preprocess.py`를 실행**해서, 본 애플리케이션에서 사용할 전처리된 데이터 `./data/emotion_talks.csv`를 생성한다.  

> [!CAUTION]
> AI허브의 사용약관에 따라 위 데이터는 GitHub에 업로드할 수 없으므로, 반드시 상기한 웹사이트에 접속하여 직접 데이터를 다운로드 받고, 압축 해제하여야 합니다.

### 3. Environment Variables

- `OPENAI_API_KEY='<your_api_key>'`
- `TEXT_CSV_PATH='./data/text.csv'`

> [!IMPORTANT]
> 반드시 `.env` 파일을 직접 만들고, 상기한 모든 환경변수를 명시해야 정상적으로 실행됩니다.  
> 자세한 사용법은 `python-dotenv` [docs](https://pypi.org/project/python-dotenv/)를 참고해주세요.

## II. Requirements

```bash
conda create -n <env-name> python=3.10
conda activate <env-name>
pip install -r requirements.txt
```

## III. Run

```bash
> streamlit run app.py
```
