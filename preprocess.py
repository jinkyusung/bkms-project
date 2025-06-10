import pandas as pd

df_train = pd.read_excel('~/Downloads/emotion_talk//Training_221115_add/original/corpus_final_training.xlsx', index_col=0)
df_valid = pd.read_excel('~/Downloads/emotion_talk/Validation_221115_add/original/corpus_final_valid.xlsx', index_col=0)
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
