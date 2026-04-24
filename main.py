import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Cursuri Udemy", layout="wide")


@st.cache_data
def load_and_filter_data(file_path):
    df = pd.read_csv(file_path)
    df_filtrat = df[df['subject'].isin(["Web Development", "Business Finance"])].copy()

    return df_filtrat

df_dev_fin = load_and_filter_data('./data/udemy_courses.csv')

# Am schimbat coloana 'published_timestamp' intr-un tip de data cu care voi putea lucra mai incolo
df_dev_fin['published_timestamp'] = pd.to_datetime(df_dev_fin['published_timestamp'])
df_dev_fin['year_published'] = df_dev_fin['published_timestamp'].dt.year



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




    # -------------- Curățarea datelor --------------

    # Tratarea valorilor null sau care ai putea distorsiona rezultatele





    st.subheader("Valorile null")
    null_count = df_dev_fin.isnull().sum().sum()
    # print(null_count)

    # În acest set de date nu am găsit deloc valori null însă am adăugat oricum o formă minimală de tratare a acestora
    if null_count > 0:
        df_nulls = df_dev_fin[df_dev_fin.isnull()]
        st.dataframe(df_nulls)

        st.warning(f"În setul de date există {null_count} valori lipsă. Rândurile care conțin aceste valori lipsă au fost eliminate.")
        df_dev_fin = df_dev_fin.dropna()
    else:
        st.info("Nu există valori null în setul de date.")





    st.subheader("Valori invalide")

    cols_numerice = df_dev_fin.select_dtypes(include=['number']).columns
    count_zeros = (df_dev_fin[cols_numerice] == 0).sum()

    df_zeros = pd.DataFrame({
        'Coloană': count_zeros.index,
        'Zerouri': count_zeros.values
    })

    df_zeros = df_zeros[df_zeros['Zerouri'] > 0].sort_values('Zerouri', ascending=False)

    fig_zeros, ax_zeros = plt.subplots(figsize=(8, 4))

    sns.barplot(data=df_zeros, y='Coloană', x='Zerouri', palette='Oranges_r', ax=ax_zeros)

    ax_zeros.set_title('Numarul celulelor cu valoarea 0 pentru fiecare coloană')
    ax_zeros.set_xlabel('Număr')
    ax_zeros.set_ylabel('Coloană')
    ax_zeros.grid(axis='x', linestyle='--', alpha=0.7)

    for container in ax_zeros.containers:
        ax_zeros.bar_label(container)

    st.pyplot(fig_zeros)

    st.write("Detalii numerice:")
    st.table(df_zeros)

    st.markdown("Se observă faptul că se întâlnesc valori de 0 în coloanele ce ilustrează date despre"
                "***preț, numărul de abonați, numărul de review-uri, numărul de lecții și durata cursului***."
                "Totuși, singurele date care din punct de vedere logic nu ar putea fi 0 sunt ***nunărul de lecții*** și ***durata cursului***."
                "Din acest motiv, cursurile cu valori de 0 în aceste coloane au fost eliminate.")








    # Tratarea cursurilor care sunt prea noi si au numar foarte mic de abonati
    # ultima_data = df_dev_fin['published_timestamp'].max()
    # prag_timp = ultima_data - pd.Timedelta(days=180)

    # Identificăm cursurile "prea noi" care au 0 abonați
    # cursuri_noi = df_dev_fin[(df_dev_fin['published_timestamp'] > prag_timp) & (df_dev_fin['num_subscribers'] == 0)]
    # no_cursuri_noi = len(cursuri_noi)
    #
    # st.write(f"Ultima actualizare în date: **{ultima_data.date()}**")
    # st.write(f"Prag de maturitate (6 luni): **{prag_timp.date()}**")
    #
    # if nr_eliminate > 0:
    #     st.warning(
    #         f"Am identificat {nr_eliminate} cursuri publicate recent care au 0 abonați. Acestea vor fi eliminate din analiza de succes.")
    #     # Păstrăm tot ce NU este în masca_zgomot
    #     df_dev_fin = df_dev_fin[~masca_zgomot].copy()
    # else:
    #     st.info("Nu au fost găsite cursuri noi cu 0 abonați care să necesite eliminare.")

    duplicate_count = df_dev_fin.duplicated(subset=['course_id']).sum()
    df_duplicate = df_dev_fin[df_dev_fin.duplicated(subset=['course_id'], keep=False)].sort_values('course_id')

    if duplicate_count > 0:
        st.write(f"Au fost găsite {duplicate_count} cursuri duplicate în setul de date inițial.")

        with st.expander("Vezi rândurile duplicate"):
            st.dataframe(df_duplicate)

        df_dev_fin = df_dev_fin.drop_duplicates(subset=['course_id'], keep='first')
        st.success("Duplicatele au fost eliminate. A fost păstrată doar prima înregistrare pentru fiecare ID.")






    st.subheader("Verificarea inconsistențelor")

    free_but_paid = df_dev_fin[(df_dev_fin['is_paid'] == False) & (df_dev_fin['price'] > 0)]
    no_free_but_paid = len(free_but_paid)
    paid_but_free = df_dev_fin[(df_dev_fin['is_paid'] == True) & (df_dev_fin['price'] == 0)]
    no_paid_but_free = len(paid_but_free)

    st.write("Coloanele care oferă informații despre prețul cursului și dacă acesta este plătit sau nu au fost testate"
             "pentru a verifica dacă există inconsistențe în rândul acestora.")

    if no_paid_but_free != 0:
        st.write(f"Au fost găsite {no_paid_but_free} cursuri marcate ca fiind gratis, dar cu preț diferit de 0.")
        with st.expander("Vezi rândurile"):
            st.dataframe(free_but_paid)
    else:
        st.write("Nu au fost găsite cursuri marcate ca fiind gratis, dar cu preț diferit de 0.")

    if no_paid_but_free != 0:
        st.write(f"Au fost găsite {no_paid_but_free} cursuri marcate ca fiind cu plată, dar cu prețul 0.")
        with st.expander("Vezi rândurile"):
            st.dataframe(paid_but_free)
    else:
        st.write("Nu au fost găsite cursuri marcate ca fiind cu plată, dar cu prețul 0.")






    # Grafice:





    # - histograma: - pentru fiecare df specific subiectului si ca variabile pentru variabila prezissa si predictori

    st.subheader("Distribuția Variabilelor: Web Development vs Business Finance")

    selected_var = st.selectbox("Alege variabila pentru care vrei să creezi histograma:",
                                ['num_subscribers', 'price', 'num_reviews', 'num_lectures', 'content_duration'])

    if selected_var:
        st.subheader(f"Analiza Distribuției pentru: {selected_var}")

        val_max_absolut = float(df_dev_fin[selected_var].max())
        val_95_percentil = float(df_dev_fin[selected_var].quantile(0.95))

        zoom_slider = st.slider(
            f"Selectează intervalul de afișare:",
            min_value=0.0,
            max_value=val_max_absolut,
            value=val_95_percentil,
            step=1.0 if val_max_absolut > 100 else 0.1
        )

        df_filtered = df_dev_fin[df_dev_fin[selected_var] <= zoom_slider]

        fig, ax = plt.subplots(figsize=(10, 5))

        sns.histplot(
            data=df_filtered,
            x=selected_var,
            hue='subject',
            element="step",
            bins=30,
            palette={'Web Development': '#1f77b4', 'Business Finance': '#ff7f0e'},
            ax=ax
        )

        ax.set_title(f"Distribuția {selected_var} (Cursuri cu valori până la {zoom_slider})")
        ax.set_xlabel(selected_var)
        ax.set_ylabel("Număr Cursuri")

        st.pyplot(fig)

        st.markdown("Toate histogramele create, cu excepția celei pentru preț au o distribuție puternic asimetrica la drapta."
                    "Acest lucru indică prezența outlierilor")





    st.subheader("Boxplots: Web Development vs Business Finance")

    var_boxplot = st.selectbox(
        "Alege variabila pentru care vrei să creezi histograma:",
        ['num_subscribers', 'price', 'content_duration', 'num_reviews']
    )

    if var_boxplot:
        zoom_outlieri = st.checkbox("Vizualizarea box-ului", value=True)

        fig_box, ax_box = plt.subplots(figsize=(10, 6))

        sns.boxplot(
            data=df_dev_fin,
            x='subject',
            y=var_boxplot,
            showmeans=True,
            palette={'Web Development': '#1f77b4', 'Business Finance': '#ff7f0e'},
            ax=ax_box
        )

        if zoom_outlieri:
            percentil_95 = df_dev_fin[var_boxplot].quantile(0.95)
            ax_box.set_ylim(0, percentil_95 * 1.5)
            st.info("Vizualizarea este limitată la percentila 95.")
        else:
            st.info("Vizualizarea boxplot-ului este completă.")

        st.pyplot(fig_box)

        st.markdown("""
        **Concluzii**
        - _Numărul de abonați_:
        În ceea ce privește numărul de abonați, față de Business Finance acest domeniu prezintă un număr mult mai mare de outlieri, mulți dintre ei fiind peste 50.000.
        Acest lucru arată că un curs de dezvoltare web are potențialul mult mai mare de a avea succes decât un curs din domeniul finanțelor.
        De asemenea, mediana cursurilor web este mai mare, deci ele sunt mai cătate.
        
        - _Preț_:
        Se observă că mediana prețului pentru ambele domenii de cursuri este aproape egală.
        Totuși, cea de-a treia cuartilă de la Web Development se află la o valoare mai mare decât cea de la Business Finance,
        ceea ce înseamnă că cele mai scumpe 25% dintre cursurile de development au prețuri mai ridicate decât același procentaj din cursurile de finanțe
        și variabilitatea prețurilor este mai amre.
        
        - _Durată_:
        Cursurile de dezvoltare necesită mai muncă și pot fi mai complexe deoarece mediana variabile content_duration are o valoare mai mare decât cea de la Business Finance.
        Tot despre cursurile tech s epoate spune că au o variabilitate mai mare întrucât cuartila a treia este semnificativ mai sus. De asemenea, ele au valori normale mai mari
        deoarece limita superioară se situează la o durată de aproximativ 14 ore, față de durata de aproximativ 8 ore de la cursurile de finance.
        De remarcat este și faptul că ambele domenii au mulți outlieri care se întind până la peste 70 de ore, cursurile de dezvoltare prezentând un outlier care atinge aproape 80 de ore.
        
        - _Numărul de recenzii_:
        Se observă că numărul de recenzii de la cursurile de web development este mai mare, mai variabil și are mult mai multi outlieri cu valori foarte mari.
        Cel mai mare outlier trece peste 25.000 de review-uri. Aceste statistici arată faptul că oamenii prezintă mult mai mult interes față de calitatea cursurilor de web decât cele de finanțe pentru afaceri.
        """)



        st.subheader("Analiza relației dintre variabila țintă (numărul de abonați) și celălalalte variabile numerice relevante")

        var_x = st.selectbox("Alege variabila pentru axa X:", ['price', 'content_duration', 'num_reviews'])
        var_y = 'num_subscribers'
        st.subheader(f"Scatter plot pentru: {var_x} vs {var_y}")

        col1, col2 = st.columns(2)

        df_web = df_dev_fin[df_dev_fin['subject'] == 'Web Development']
        df_finance = df_dev_fin[df_dev_fin['subject'] == 'Business Finance']

        with col1:
            st.write("**Web Development**")
            fig_web, ax_web = plt.subplots()
            sns.scatterplot(data=df_web, x=var_x, y=var_y, color='#1f77b4', alpha=0.6, ax=ax_web)
            ax_web.set_title("Web Development")
            st.pyplot(fig_web)

        with col2:
            st.write("**Business Finance**")
            fig_fin, ax_fin = plt.subplots()
            sns.scatterplot(data=df_finance, x=var_x, y=var_y, color='#ff7f0e', alpha=0.6, ax=ax_fin)
            ax_fin.set_title("Business Finance")
            st.pyplot(fig_fin)

        st.markdown("""
        - Relația dintre numărul de abonați și prețul cursului: Atât pentru Business Finance, cât și pentru Web Development se observă
        faptul că există o oarecare pantă negativă. Majoritatea cursurilor se aglomerează în intervalul de preț 0 - 60$ și multe au un număr destul de mare de abonați.
        Pentru cursurile gratis se disting outlieri deosebiți, cursuri cu peste 100.000 de mii de abonați și chiar peste 250.000 pentru Web Development
        și cursuri cu peste 10.000 de abonați și chiar peste 60.000 pentru cursurile de Finance. Ca o concluzie, pe piața cursurilor online, cursurile care sunt gratuite sunt mult mai atractive și mai achiziționate.
        De remarcat este faptul că și zona cu prețul cuprins între 175 și 200 prezintp cursuri cu un număr crescut de abonați, în mode special cele apropiate de 200.
        Ele pot fi cursuri care complexe, care deși au un preț mare, sunt apreciate de cumpărători.
        - Relația dintre numărul de abonați și durata în ore:
        Se observă clar faptul că pe măsură ce durata cursului crește, numărul de abonați scade. Acest lucru este de așteptat considerând că un curs mult mai lung necesită mult mai multă implicare.
        Existp foarte multe cursuri concentarre între 0 și 20 ore pentru development, iar această secțiune include și cursurile putlier cu număr deosebit de mare de abonați.
        După 30 de ore, numărul de abonați scade brusc, existând totuși câteva excepții, precum cursul de aproximativ 40 de ore care are aprocimativ 125.000 de abonați.
        Șa finanțe, intervalul concentrării se reduce la 0-5 ore, iar după pragul de 15 ore, variabila scade aproape spre 0. Comparativ cu dev, piața cursurilor de business este și mai rezistentă la cursurile de lungă durată.
        - Relația dintre numărul de abonați și num[rul de recenzii:
        Se observă că cu cât există mai multe review-uri, cu atât există mai mulți abonați (relație pozitivă), adică oamenii se bazează faoarte mult pe acest indicator social atunci când decid cumpărarea unui curs.
        Atât pentru dev, cât și pentru fin rezultatele sunt aglomerate în colțul din stânga sus, adică sunt multe cursuri cu popularitate mică,
        iar cursurile cu popularitate mare sunt împrăștiate. Interesant este câ acel curs viral de Web Development,
        în comparație cu numărul mare de abonați (peste 250.000), are relativ puține review-uri (sub 10.000). Aceeași situație se remarcă și la Finance. 
        """)











