import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cursuri Udemy", layout="wide")


@st.cache_data
def load_and_filter_data(file_path):
    df = pd.read_csv(file_path)
    df_filtrat = df[df['subject'].isin(["Web Development", "Business Finance"])].copy()

    return df_filtrat

df_dev_fin = load_and_filter_data('./data/udemy_courses.csv')



st.title("Analiza factorilor de succes ai cursurilor onlinede pe platforma Udemy")
st.markdown("""
Această aplicație analizează factorii care influențează succesul cursurilor pe platforma Udemy, 
comparând domeniile cele mai întâlnite în setul de date: **Web Development** și **Business Finance**.
""")


sectiune = st.sidebar.radio("Secțiuni:", ["Introducere și date inițiale", "Analiza exploratorie a seturilor de date"])

if sectiune == "Introducere și date inițiale":

    st.subheader("Datele inițiale:")
    st.write(df_dev_fin)

    st.write(f"Numărul total de cursuri este de {df_dev_fin.shape[0]}.")
    # tab_dev, tab_fin = st.tabs(["Cursuri de Web Development", "Cursuri de Business Finance"])
    # with tab_dev:

    st.subheader("Distribuția cursurilor pe domenii")
    st.write(df_dev_fin['subject'].value_counts())



elif sectiune == "Analiza exploratorie a seturilor de date":
    st.header("Analiza exploratorie")


    null_count = df_dev_fin.isnull().sum().sum()
    # print(null_count)

    # În acest set de date nu am găsit deloc valori null însă am adăugat oricum o formă minimală de tratare a acestora
    if null_count > 0:
        st.warning(f"În setul de date există {null_count} valori lipsă. Acestea au fost tratate prin eliminare.")
        df_dev_fin = df_dev_fin.dropna()
    else:
        st.info("Nu există valori null în setul de date.")

    duplicate_count = df_dev_fin.duplicated(subset=['course_id']).sum()
    if duplicate_count > 0:
        print(duplicate_count)
        st.write(f"Au fost găsite {duplicate_count} cursuri duplicate în setul de date inițial. Acestea au fost tratate prin eliminare.")
        df_dev_fin = df_dev_fin.drop_duplicates(subset=['course_id'])


    st.subheader("Verificarea inconsistențelor")

    free_but_paid = len(df_dev_fin[(df_dev_fin['is_paid'] == False) & (df_dev_fin['price'] > 0)])
    paid_but_free = len(df_dev_fin[(df_dev_fin['is_paid'] == True) & (df_dev_fin['price'] == 0)])

    col1, col2 = st.columns(2)
    col1.metric("Cursuri care sunt marcate ca fiind gratis însă au preț diferit de 0", free_but_paid)
    col1.metric("Cursuri care sunt marcate ca fiind plătite însă au preț 0", paid_but_free)
