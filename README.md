# 감정분석 챗봇

## Structure

### Directory

```bash
project-root/
├── data/
│   └── text.csv
├── .env
├── .gitignore
├── README.md
├── app.py
├── procedure.py
└── requirements.txt
```

### Environment variables

- `OPENAI_API_KEY`
- `TEXT_CSV_PATH`

> [!IMPORTANT]
> 반드시 `.env` 파일을 직접 만들고, 상기한 모든 환경변수를 명시해야 정상적으로 실행됩니다.  
> 자세한 사용법은 `python-dotenv` [docs](https://pypi.org/project/python-dotenv/)를 참고해주세요.

## Requirements

```bash
conda create -n <env-name> python=3.10
conda activate <env-name>
pip install -r requirements.txt
```

## Run

```bash
> streamlit run app.py
```
