import pandas as pd

# Path
path_trn = './data/감성대화말뭉치(최종데이터)_Training.xlsx'
path_val = './data/감성대화말뭉치(최종데이터)_Validation.xlsx'

df_train = pd.read_excel(path_trn, index_col=0)
df_valid = pd.read_excel(path_val, index_col=0)
df_all = pd.concat([df_train, df_valid], ignore_index=True)

emotions = ['감정_대분류', '감정_소분류']
human_speeches = ['사람문장1', '사람문장2']
columns_to_keep = emotions + human_speeches

df_all['human_speech'] = df_all[human_speeches].apply(lambda row: ' '.join(row.astype(str)), axis=1)
df_all = df_all[['감정_대분류', '감정_소분류', 'human_speech']].rename(columns={
    '감정_대분류': 'major_emotion',
    '감정_소분류': 'minor_emotion'
})

df_all.to_csv('./data/emotion_talks.csv')
