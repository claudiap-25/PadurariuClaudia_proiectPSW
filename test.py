import pandas as pd

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