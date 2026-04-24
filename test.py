import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("data/udemy_courses.csv")
df_dev_fin = df[df['subject'].isin(["Web Development", "Business Finance"])].copy()

null_count = df_dev_fin.isnull().sum().sum()
print(f"Nulls: {null_count}")


duplicate_count = df_dev_fin[df_dev_fin.duplicated(subset=['course_id'])]
print(f"Dps: {duplicate_count}")
print(f"Dps count: {len(duplicate_count)}") # 5 duplicate

free_but_paid = len(df_dev_fin[(df_dev_fin['is_paid'] == False) & (df_dev_fin['price'] > 0)])
paid_but_free = len(df_dev_fin[(df_dev_fin['is_paid'] == True) & (df_dev_fin['price'] == 0)])

print("Cursuri care sunt marcate ca fiind gratis însă au preț diferit de 0:", free_but_paid)
print("Cursuri care sunt marcate ca fiind plătite însă au preț 0:", paid_but_free)




df_dev_fin['published_timestamp'] = pd.to_datetime(df_dev_fin['published_timestamp'])
df_dev_fin['year_published'] = df_dev_fin['published_timestamp'].dt.year
ultima_data = df_dev_fin['published_timestamp'].min()
print(ultima_data)

ultima_data = df_dev_fin['published_timestamp'].max()
prag_timp = ultima_data - pd.Timedelta(days=180)


# Identificăm cursurile "prea noi" care au 0 abonați
cursuri_noi = df_dev_fin[(df_dev_fin['published_timestamp'] > prag_timp) & (df_dev_fin['num_subscribers'] == 0)]
no_cursuri_noi = len(cursuri_noi)
print("\nCursuri noi ", no_cursuri_noi)





# cols_numerice = df_dev_fin.select_dtypes(include=['number']).columns
# count_zeros = (df_dev_fin[cols_numerice] == 0).sum()
#
# df_zeros = pd.DataFrame({
#     'Coloană': count_zeros.index,
#     'Zerouri': count_zeros.values
# })
#
# df_zeros = df_zeros[df_zeros['Zerouri'] > 0].sort_values('Zerouri', ascending=False)
#
# fig_zeros, ax_zeros = plt.subplots(figsize=(8, 4))
#
# sns.barplot(data=df_zeros, y='Coloană', x='Zerouri', palette='Oranges_r', ax=ax_zeros)
#
# ax_zeros.set_title('Numarul celulelor cu valoarea 0 pentru fiecare coloană')
# ax_zeros.set_xlabel('Număr')
# ax_zeros.set_ylabel('Coloană')
# ax_zeros.grid(axis='x', linestyle='--', alpha=0.7)
#
# for container in ax_zeros.containers:
#     ax_zeros.bar_label(container)
#
# plt.show()




null_count = df_dev_fin.isnull()

