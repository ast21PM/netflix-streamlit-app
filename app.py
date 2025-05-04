import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


@st.cache_data
def load_data():
    return pd.read_csv('data/netflix_titles.csv')

df = load_data()


st.set_page_config(page_title="Netflix Analytics", layout="wide")
st.title("📊 Netflix Content Analysis Dashboard")
st.markdown("""
Анализ каталога Netflix с использованием данных из Kaggle.
* **Источник данных:** [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)
* **Автор:** [Ваше имя]
""")


with st.sidebar:
    st.header("Фильтры")
    selected_type = st.selectbox(
        "Тип контента",
        ['All', 'Movie', 'TV Show'],
        index=0
    )
    
    year_range = st.slider(
        "Год выпуска",
        1940, 2022,
        (2010, 2022)
    )
    
    countries = df['country'].dropna().unique()
    selected_countries = st.multiselect(
        "Страны производства",
        options=countries,
        default=[]
    )
    
    show_stats = st.checkbox("Показать статистику")
    search_query = st.text_input("Поиск по названию")


filtered_data = df[
    (df['type'] == selected_type) if selected_type != 'All' else True
] 
filtered_data = filtered_data[
    filtered_data['release_year'].between(*year_range)
]
if selected_countries:
    filtered_data = filtered_data[
        filtered_data['country'].isin(selected_countries)
    ]
if search_query:
    filtered_data = filtered_data[
        filtered_data['title'].str.contains(search_query, case=False)
    ]


col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Всего контента", len(filtered_data))
with col2:
    avg_duration = filtered_data['duration'].mean() if selected_type == 'Movie' else None
    st.metric("Средняя длительность", f"{avg_duration:.1f} мин" if avg_duration else "N/A")
with col3:
    st.metric("Самый старый релиз", filtered_data['release_year'].min())


st.subheader("Распределение по рейтингам")
fig, ax = plt.subplots()
filtered_data['rating'].value_counts().plot(kind='bar', ax=ax)
st.pyplot(fig)

st.subheader("Таблица данных")
st.dataframe(
    filtered_data[['title', 'type', 'release_year', 'country', 'duration']],
    height=400,
    use_container_width=True
)


if show_stats:
    st.subheader("Дополнительная статистика")
    st.write("Топ-10 стран по производству:")
    st.bar_chart(filtered_data['country'].value_counts().head(10))
