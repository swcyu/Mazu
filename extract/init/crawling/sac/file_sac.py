import pandas as pd

df = pd.read_csv('./sac_data/SAC1.csv', encoding='euc-kr')
df.drop(['번호'], axis=1, inplace=True)

for i in range(2, 13):
    df_add = pd.read_csv('./sac_data/SAC'+str(i)+'.csv', encoding='euc-kr')
    df_add.drop(['번호'], axis=1, inplace=True)
    df = pd.concat([df, df_add])

# print(df.columns)
# print(df)

df.to_csv('sac_list.csv', encoding="utf-8-sig")