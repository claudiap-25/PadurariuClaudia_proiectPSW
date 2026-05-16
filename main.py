import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

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



df_web = df_dev_fin[df_dev_fin['subject'] == 'Web Development']
df_fin = df_dev_fin[df_dev_fin['subject'] == 'Business Finance']



st.title("Analiza factorilor de succes ai cursurilor online de pe platforma Udemy")
st.markdown("""
Această aplicație analizează factorii care influențează succesul cursurilor pe platforma Udemy, 
comparând domeniile cele mai întâlnite în setul de date: **Web Development** și **Business Finance**.
""")


sectiune = st.sidebar.radio("Secțiuni:", ["Introducere și date inițiale", "Analiza exploratorie a seturilor de date"], key="sidebar_radio")

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
    cols_numerice = cols_numerice.drop(["course_id", "year_published"])

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

    linii_invalide = (df_dev_fin['num_lectures'] == 0) | (df_dev_fin['content_duration'] == 0)
    nr_eliminate = linii_invalide.sum()

    if nr_eliminate > 0:
        # Păstrăm doar rândurile care NU sunt invalide
        df_dev_fin = df_dev_fin[~linii_invalide].copy()
        st.success(f"Au fost eliminate {nr_eliminate} cursuri cu date invalide (0 lecții sau 0 durată).")
    else:
        st.info("Nu au fost găsite cursuri cu 0 lecții sau 0 durată.")






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
        st.subheader("Distribuția Variabilelor numerice: Web Development vs Business Finance")

        selected_var = st.selectbox("Alege variabila pentru care vrei să creezi histograma:",
                                    ['num_subscribers', 'price', 'num_reviews', 'num_lectures', 'content_duration'])

        if selected_var:
            st.subheader(f"Analiza Distribuției pentru: {selected_var}")

            # Calculăm limitele absolute pentru a defini marginile slider-ului
            val_min_abs = float(df_dev_fin[selected_var].min())
            val_max_abs = float(df_dev_fin[selected_var].max())
            # Calculăm percentila 95 pentru a oferi o setare inițială (default) utilă
            val_95_percentil = float(df_dev_fin[selected_var].quantile(0.95))

            # Transformăm slider-ul într-unul de interval (range slider)
            # prin transmiterea unui tuplu la parametrul 'value'
            interval_slider = st.slider(
                f"Selectează intervalul de valori (Min - Max):",
                min_value=val_min_abs,
                max_value=val_max_abs,
                value=(val_min_abs, val_95_percentil),  # Setarea inițială: de la minim la 95% din date
                step=1.0 if val_max_abs > 100 else 0.1
            )

            # Filtrarea dataframe-ului folosind ambele capete ale intervalului
            # interval_slider[0] este valoarea minimă selectată, [1] este cea maximă
            df_filtered = df_dev_fin[
                (df_dev_fin[selected_var] >= interval_slider[0]) &
                (df_dev_fin[selected_var] <= interval_slider[1])
                ]

            subjects_in_data = df_filtered['subject'].unique()

            if len(df_filtered) == 0:
                st.warning("Nu există cursuri în acest interval. Selectează un interval mai larg.")
            elif len(subjects_in_data) < 2:
                # Dacă avem doar un subiect, desenăm graficul fără parametrul 'hue' sau cu o avertizare
                st.info(f"În acest interval există doar cursuri de {subjects_in_data[0]}.")

                fig_corr, ax = plt.subplots(figsize=(10, 5))
                sns.histplot(data=df_filtered, x=selected_var,
                             color='#1f77b4' if subjects_in_data[0] == 'Web Development' else '#ff7f0e', ax=ax)
                st.pyplot(fig_corr)
            else:
                # Codul tău original care funcționează când ambele subiecte sunt prezente
                fig_corr, ax = plt.subplots(figsize=(10, 5))
                sns.histplot(
                    data=df_filtered,
                    x=selected_var,
                    hue='subject',
                    element="step",
                    common_norm=False,
                    bins=30,
                    palette={'Web Development': '#1f77b4', 'Business Finance': '#ff7f0e'},
                    ax=ax
                )
                ax.set_title(f"Distribuția {selected_var} între {interval_slider[0]} și {interval_slider[1]}")
                st.pyplot(fig_corr)

        st.markdown("La o primă vedere se observă că toate histogramele create, cu excepția celei pentru preț au o distribuție puternic asimetrica la drapta."
            "Prin restrângerea intervalului pentru valoarile variabilei analizate, se observă faptul că cursurile de Business Finance tind să se concentreze"
            "în zone cu valori mici, cu mult mai puține valori extreme, față de cursurile de Web Development unde valorile sunt mult mai împrăștiate și concentrate pe valori mai depărtate de 0."
            "De exemplu, pentru numărul de abonați se observă că bara histogramei pentru cursurile cu foarte puțini abonați (mai puțin de 1000) este cu mult mai mare decît cea pentru cursurile de dezvoltare și că numărul cursurilor de dezvoltare tinde să fie mai mare pentru numerele mai mari de abonați."
            "Dacă restrângem histograma la valori foarte mari, vom regăsi numai cursuri de dezvoltare Web."
            "Asemănător se întâmplă pentru toate celălalte variabile asimetric distribuite."
            "În ceea ce privește numărul de abonați și numărul de recenzii, această parituclaritate a histogramelor arată că sunt mai mulți utilizatori care caută și manifestă interes față de cursuril de Web Development decăt pentru cele de Finance."
            "Din punctul de vedere al duratei cursului și al numărului de lecții dintr-un curs, se poate deduce că cursurile de Finance nu necesistă la fel de mult efort și timp precum cele de programare."
            )



        st.subheader("Distribuția Variabilelor Categorice: Web Development vs Business Finance")

        # Selectăm variabilele categorice relevante
        var_categorica = st.selectbox(
            "Alege variabila categorică pentru analiză:",
            ['level', 'is_paid', 'year_published']
        )

        if var_categorica:
            col_web, col_fin = st.columns(2)

            # Pregătim datele pentru a asigura aceeași ordine a categoriilor în ambele grafice
            order = df_dev_fin[var_categorica].value_counts().index

            with col_web:
                st.write(f"**Web Development: {var_categorica}**")
                fig_web, ax_web = plt.subplots(figsize=(8, 5))
                sns.countplot(
                    data=df_dev_fin[df_dev_fin['subject'] == 'Web Development'],
                    x=var_categorica,
                    order=order,
                    palette='Blues_d',
                    ax=ax_web
                )
                plt.xticks(rotation=45)
                st.pyplot(fig_web)

            with col_fin:
                st.write(f"**Business Finance: {var_categorica}**")
                fig_fin, ax_fin = plt.subplots(figsize=(8, 5))
                sns.countplot(
                    data=df_dev_fin[df_dev_fin['subject'] == 'Business Finance'],
                    x=var_categorica,
                    order=order,
                    palette='Oranges_d',
                    ax=ax_fin
                )
                plt.xticks(rotation=45)
                st.pyplot(fig_fin)

            st.markdown("""
            **Concluzii**
            - _level_: Se observă că distribuția numărului de cursuri în funcție de categorii este foarte asemănătoare pentru ambele cursuri, cele de finanțe având frecvențe puțin mai mari. Cele mai des întâlnite tipuri sunt cele care acoperă toate nivelurile de cunoștințe, iar cele mai rare sunt cele pentru experți.
            - _is_paid_: Pentru ambele categorii predomină cursurile cu plată.
            - _year_published_: Se observă că odată cu înaintarea în timp au apărut din ce în ce mai multe cursuri pe piața Udemy. În 2016, numărul cursurilor de programare publicate întrece pragul de 450, pe când cel pentru cursurile de Finance este puțin sub 350. Anul precedent arată un număr asemănptor de publicații pentru cursurile de Business Finance, față de Web Development unde diferența este de aproximativ 100.
            """)


    st.subheader("Boxplots: Web Development vs Business Finance")

    var_boxplot = st.selectbox(
        "Alege variabila pentru care vrei să creezi boxplot-ul:",
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
        De asemenea, mediana cursurilor web este mai mare, deci ele sunt mai căutate.
        
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


        def plot_boxplot_cat_numeric(df, cat_col, num_col, subject_name, color_palette):

            fig, ax = plt.subplots(figsize=(8, 4))
            sns.boxplot(data=df, x=cat_col, y=num_col, palette=color_palette, ax=ax)

            # Adăugăm limitare pentru vizibilitate (percentila 95) din cauza outlierilor mari
            percentil_95 = df[num_col].quantile(0.95)
            ax.set_ylim(0, percentil_95 * 1.5)

            ax.set_title(f"{subject_name}: {num_col} în funcție de {cat_col}")
            ax.set_xlabel(cat_col)
            ax.set_ylabel(num_col)
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Afișare în Streamlit
            st.pyplot(fig)


        st.subheader("Analiza succesului (num_subscribers) în funcție de Nivel")

        numeric_col = 'num_subscribers'
        cat_cols = ['level']  # Poți adăuga și 'is_paid' aici dacă vrei mai multe diagrame

        col_web, col_fin = st.columns(2)

        with col_web:
            st.write("**Web Development**")
            df_web = df_dev_fin[df_dev_fin['subject'] == 'Web Development']
            for cat_col in cat_cols:
                if cat_col in df_web.columns:
                    plot_boxplot_cat_numeric(df_web, cat_col, numeric_col, "Web Dev", 'viridis')

        with col_fin:
            st.write("**Business Finance**")
            df_finance = df_dev_fin[df_dev_fin['subject'] == 'Business Finance']
            for cat_col in cat_cols:
                if cat_col in df_finance.columns:
                    plot_boxplot_cat_numeric(df_finance, cat_col, numeric_col, "Business Finance", 'magma')


        st.markdown("""
        Web Development: Predomină cursurile de tip "All Levels" și "Beginner". Acest lucru sugerează că, odată cu dezvoltarea tehnologiei, oamenilor le-a fost sporit interesul pentru cunoașterea acestui domeniu, eventual orientare profesională, și atunci aceștia se îndreaptă cătrec cursurile introductive sau potivite pentru toate nivelele de cunoștințe.
        Business Finance: Predomină și aici cursurile de tip "All Levels" și "Beginner", însă la acestea se adaugă și nivelul de "Expert". Acest lucru sugerează faptul că utilizatorii din domeniul de finanțe sunt mai interesați să aprofundeze cunoștințele sau să se specializeze.
        """)





        st.subheader("Analiza relației dintre variabila țintă (numărul de abonați) și celălalalte variabile numerice relevante")

        var_x = st.selectbox("Alege variabila pentru axa X:", ['price', 'content_duration', 'num_reviews'])
        var_y = 'num_subscribers'
        st.subheader(f"Scatter plot pentru: {var_x} vs {var_y}")

        col1_iqr, col2_iqr = st.columns(2)

        df_web = df_dev_fin[df_dev_fin['subject'] == 'Web Development']
        df_finance = df_dev_fin[df_dev_fin['subject'] == 'Business Finance']

        with col1_iqr:
            st.write("**Web Development**")
            fig_web, ax_web = plt.subplots()
            sns.scatterplot(data=df_web, x=var_x, y=var_y, color='#1f77b4', alpha=0.6, ax=ax_web)
            ax_web.set_title("Web Development")
            st.pyplot(fig_web)

        with col2_iqr:
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



        st.subheader("Detectarea Outlierilor prin Metoda IQR")


        cols_outlieri = ['num_subscribers', 'num_reviews', 'content_duration', 'num_lectures']

        col_selectata = st.selectbox(
            "Alege variabila pentru analiza outlierilor:",
            cols_outlieri,
            key="selectbox_outlieri_iqr"
        )


        def calcul_iqr(df, coloana):
            Q1 = df[coloana].quantile(0.25)
            Q3 = df[coloana].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outlieri = df[(df[coloana] < lower) | (df[coloana] > upper)]
            outlieri.sort_values(by=[coloana], inplace=True, ascending=False)
            return outlieri, lower, upper, Q1, Q3, IQR

        def grupare(df, coloana):
            return df.groupby(by=[coloana])['course_title'].count()



        outlieri_web, lower_web, upper_web, Q1_web, Q3_web, IQR_web = calcul_iqr(df_web, col_selectata)
        outlieri_fin, lower_fin, upper_fin, Q1_fin, Q3_fin, IQR_fin = calcul_iqr(df_finance, col_selectata)

        col1_iqr, col2_iqr = st.columns(2)

        for col_ui, (subject, df_sub, culoare, outlieri_df, lower_bound, upper_bound, Q1, Q3, IQR) in zip(
                [col1_iqr, col2_iqr],
                [
                    ("Web Development", df_web, '#1f77b4', outlieri_web, lower_web, upper_web, Q1_web, Q3_web, IQR_web),
                    ("Business Finance", df_finance, '#ff7f0e', outlieri_fin, lower_fin, upper_fin, Q1_fin, Q3_fin, IQR_fin)
                ]
        ):
            with col_ui:
                st.write(f"**{subject}**")
                st.table(pd.DataFrame(data=[Q1, Q3, IQR, lower_bound, upper_bound], index=["Q1", "Q3", "IQR", "lower_bound", "upper_bound"]))

                st.write(
                    f"Număr outlieri: {len(outlieri_df)} ({round(len(outlieri_df) / len(df_sub) * 100, 1)}% din totalul de cursuri")

                st.dataframe(outlieri_df)

        if col_selectata == "num_subscribers":
            st.markdown("#### Analiza suplimentară a cursurilor cu număr mare de abonați")

            optiune_grupare = st.radio("Grupează cursurile outlier după:", ["nivel", "an", "gratuitate"],
                                       key="group_radio")

            col1_grup, col2_grup = st.columns(2)

            with col1_grup:
                st.write("**Web Development**")
                if optiune_grupare == "nivel":
                    st.dataframe(grupare(outlieri_web, "level"))
                if optiune_grupare == "an":
                    st.dataframe(grupare(outlieri_web, "year_published"))
                if optiune_grupare == "gratuitate":
                    st.dataframe(grupare(outlieri_web, "is_paid"))

            with col2_grup:
                st.write("**Business Finance**")
                if optiune_grupare == "nivel":
                    st.dataframe(grupare(outlieri_fin, "level"))
                if optiune_grupare == "an":
                    st.dataframe(grupare(outlieri_fin, "year_published"))
                if optiune_grupare == "gratuitate":
                    st.dataframe(grupare(outlieri_fin, "is_paid"))

            st.markdown("""
            - _nivel_: Se observă faptul că și în rândul cursurilor cu număr foarte mare de abonați, preferința cea mai mare este pentru cele destinate
            tuturor nivelurilor de cunoștințe, următoarele cele mai căutate fiind cele entry-level, pentru ambele tipuri de cursuri.
            - _an_: Cele mai multe cursuri outlier au fost pubșicate în anul 2015, pentru Web Development și 2014 pentru Finance. Cursurile outlier din anii mai noi,
            deși probabil sunt mai evoluate din punct de vedere al conținutului prezentat, nu a trecut îndeajuns de mult timp de la data publicării până la data întocmirii setului de date studiat
            pentru a căpăta viziibilitate.
            - _gratuitate_: Chiar și în cazul cursurilor outlier, se observă că preferința mult mai mare este pentru cele plătite. 
            Acest lucru se poate datora faptului că un curs plătit denotă calitate mai mare, crescându-se astfel încrederea cumpărătorilor,
            """)




        st.write("Analiza efectuată până acum arată că domeniul de dezvoltare web este mai dezvoltat decât cel al finanțelor de business."
                 "Oamenii prezintă un interes general mai crescut pentru programare, iteracțiunea cu astfel de planuri de învățământ este mai mare, iar datele sunt mult mai variate."
                 "Din acest motiv, studiul se va concentra în continuare doar pe cursurile din domeniul Web Development și vor fi analizate separat, dar comparativ cursurile normale și cele outlier.")
        st.write("În următoarele etape vom pregăti seturile de date pentru regresie")

        df_ml = df_web.copy()

        Q1 = df_ml['num_subscribers'].quantile(0.25)
        Q3 = df_ml['num_subscribers'].quantile(0.75)
        IQR = Q3 - Q1
        upper = Q3 + 1.5 * IQR

        df_ml_piata_normala = df_ml[df_ml['num_subscribers'] <= upper]
        df_ml_piata_virala = df_ml[df_ml['num_subscribers'] > upper]



        st.subheader("Analiza corelației între variabilele numerice pentru cele două tipuri de piață")
        col_norm, col_vir = st.columns(2)

        with col_norm:
            st.write("**Piața Normală (Cursuri standard)**")
            # Calculăm corelația pentru piața normală (conține încă num_lectures pentru grafic)
            matr_corr_norm = df_ml_piata_normala[cols_numerice].corr()

            fig_norm, ax_norm = plt.subplots(figsize=(8, 6))
            sns.heatmap(matr_corr_norm, annot=True, cmap='coolwarm', fmt=".2f", ax=ax_norm, cbar=False)
            ax_norm.set_title("Matrice Corelație - Piața Normală")
            st.pyplot(fig_norm)

        with col_vir:
            st.write("**Piața Virală (Outlieri de succes)**")
            # Calculăm corelația pentru piața virală
            matr_corr_vir = df_ml_piata_virala[cols_numerice].corr()

            fig_vir, ax_vir = plt.subplots(figsize=(8, 6))
            sns.heatmap(matr_corr_vir, annot=True, cmap='coolwarm', fmt=".2f", ax=ax_vir)
            ax_vir.set_title("Matrice Corelație - Piața Virală")
            st.pyplot(fig_vir)

        st.write("În ambele heatmap-uri se observă o corelație foarte ridicată intre numărul de lecții pe care le conține un curs și durata acestuia."
                 " Pentru a nu genera multicoliniaritate la nivelul regresiei trebuie eliminată una dintre variabile. "
                 "Întrucât numărul de ore oferă o imagine mai realistă asupra nivelului de efort care trebuie depus, "
                 "vom păstra această variabilă și o vom elimina pe cea care reprezintă numărul de lecții."
                 ""
                 "De remarcat este faptul că pe piața cursurilor virale, variabilele numerice au o influență mai mare asupra numărului de abonați, comparativ cu piața normală."
                 "Numărul de recenzii, deși important și în primul heatmap, în cel de-al doilea devine și mai important pentru numărul deoameni care decid să achiziționeze cursul."
                 "O altă variabilă care crește destul de mult în analiza cursurilor virale este prețul.")

        # df_ml_piata_normala = df_ml_piata_normala.drop(columns=['num_lectures'])
        # df_ml_piata_virala = df_ml_piata_virala.drop(columns=['num_lectures'])
        df_ml = df_ml.drop(columns=['num_lectures'])
        cols_numerice = [col for col in cols_numerice if col != 'num_lectures']


        st.subheader("Feature engineering")
        st.write("Din data publicării putem extrage încă douî informații folositoare, pe lângă anul publicării: vechimea cursului și luna în care acesta a fost publicat.")

        data_maxima = df_ml['published_timestamp'].max()
        df_ml['course_age_days'] = (data_maxima - df_ml['published_timestamp']).dt.days
        df_ml['month_published'] = df_ml['published_timestamp'].dt.month

        st.dataframe(df_ml)





        st.subheader("Codificarea variabilelor categorice (encodarea)")
        st.write(
            "Transformăm variabilele 'level' și 'month_published' în variabile dummy pentru a le introduce în regresie.")

        df_ml_encoded = pd.get_dummies(df_ml, columns=['level', 'month_published'], drop_first=True, dtype=int)


        st.dataframe(df_ml_encoded)


        # refacem impartirea
        df_ml_piata_normala = df_ml_encoded[df_ml_encoded['num_subscribers'] <= upper]
        df_ml_piata_virala = df_ml_encoded[df_ml_encoded['num_subscribers'] > upper]


        st.subheader("Standardizare datelor")


        cols_to_scale = ['price', 'content_duration', 'course_age_days']


        df_norm_scaled = df_ml_piata_normala.copy()
        scaler_normal = StandardScaler()
        df_norm_scaled[cols_to_scale] = scaler_normal.fit_transform(df_ml_piata_normala[cols_to_scale])


        df_vir_scaled = df_ml_piata_virala.copy()
        scaler_viral = StandardScaler()
        df_vir_scaled[cols_to_scale] = scaler_viral.fit_transform(df_ml_piata_virala[cols_to_scale])






