import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from io import StringIO

st.set_page_config(page_title="Netflix Analytics", layout="wide")

@st.cache_data
def load_data():
    try:
        file_path = 'data/netflix_titles.csv'
        if not os.path.exists(file_path):
            st.error(f"Файл {file_path} не найден!")
            return pd.DataFrame()
        df = pd.read_csv(file_path)
        if 'country' not in df.columns:
            df['country'] = 'Unknown'
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки: {str(e)}")
        return pd.DataFrame()

df = load_data()

if not isinstance(df, pd.DataFrame):
    st.error("Критическая ошибка: Не удалось инициализировать DataFrame")
    st.stop()

st.title("📊 Netflix Content Analysis Dashboard")
st.markdown("""
Анализ каталога Netflix с использованием данных из Kaggle.
* Источник данных: [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)
* Автор: [ast_57]
""")

with st.sidebar:
    st.header("Фильтры")
    
    min_year = 1925
    max_year = 2022
    
    if not df.empty and 'release_year' in df.columns:
        min_year = int(df['release_year'].min())
        max_year = int(df['release_year'].max())

    year_range = st.slider(
        "Год выпуска",
        min_year, max_year,
        (min_year, max_year)
    )
    
    countries = ['All'] + sorted(df['country'].dropna().unique().tolist()) if 'country' in df.columns else ['All']
    selected_countries = st.multiselect(
        "Страны производства",
        options=countries,
        default=['All']
    )

    selected_type = st.selectbox("Тип контента", options=['All', 'Movie', 'TV Show'])
    
    genres = ['All'] + sorted(set([genre.strip() for genres in df['listed_in'].dropna() for genre in genres.split(',')]))
    selected_genres = st.multiselect("Жанры", options=genres, default=['All'])
    
    show_stats = st.checkbox("Показать статистику")
    search_query = st.text_input("Поиск по названию")

try:
    filtered_data = df.copy()
    
    if selected_type != 'All':
        filtered_data = filtered_data[filtered_data['type'] == selected_type]
    
    filtered_data = filtered_data[
        filtered_data['release_year'].between(year_range[0], year_range[1])
    ]
    
    if 'All' not in selected_countries and 'country' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['country'].isin(selected_countries)]
    
    if 'All' not in selected_genres and 'listed_in' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['listed_in'].str.contains('|'.join(selected_genres), case=False, na=False)]
    
    if search_query and 'title' in filtered_data.columns:
        filtered_data = filtered_data[
            filtered_data['title'].str.contains(search_query, case=False, na=False)
        ]

except Exception as e:
    st.error(f"Ошибка фильтрации: {str(e)}")
    filtered_data = df.copy()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Всего контента", len(filtered_data))

with col2:
    if selected_type == 'Movie' and 'duration' in filtered_data.columns:
        try:
            duration = filtered_data['duration'].str.extract(r'(\d+)')[0].astype(float)
            avg_duration = duration.mean()
            st.metric("Средняя длительность", f"{avg_duration:.1f} мин" if pd.notna(avg_duration) else "Нет данных")
        except Exception as e:
            st.metric("Средняя длительность", "Нет данных")
    elif selected_type == 'TV Show' and 'duration' in filtered_data.columns:
        try:
            seasons = filtered_data['duration'].str.extract(r'(\d+)')[0].astype(float)
            avg_seasons = seasons.mean()
            st.metric("Среднее кол-во сезонов", f"{avg_seasons:.1f}" if pd.notna(avg_seasons) else "Нет данных")
        except Exception as e:
            st.metric("Среднее кол-во сезонов", "Нет данных")
    else:
        st.metric("Средняя длительность", "Не применимо")

with col3:
    release_year = filtered_data['release_year'].min() if not filtered_data.empty else "Нет данных"
    st.metric("Самый старый релиз", release_year)

if show_stats and not filtered_data.empty:
    st.subheader("Дополнительная статистика")
    
    type_counts = filtered_data['type'].value_counts()
    st.write("**Распределение по типу контента:**")
    st.write(f"- Фильмы: {type_counts.get('Movie', 0)}")
    st.write(f"- Сериалы: {type_counts.get('TV Show', 0)}")
    
    if 'release_year' in filtered_data.columns:
        avg_year = filtered_data['release_year'].mean()
        st.write(f"**Средний год выпуска:** {avg_year:.1f}" if pd.notna(avg_year) else "**Средний год выпуска:** Нет данных")
    
    if 'listed_in' in filtered_data.columns:
        genres_list = [genre.strip() for genres in filtered_data['listed_in'].dropna() for genre in genres.split(',')]
        genre_counts = pd.Series(genres_list).value_counts().head(1)
        st.write("**Самый популярный жанр:**")
        for genre, count in genre_counts.items():
            st.write(f"- {genre}: {count}")

st.subheader("Распределение по годам выпуска")
if not filtered_data.empty and 'release_year' in filtered_data.columns:
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        filtered_data['release_year'].value_counts().sort_index().plot(kind='line', ax=ax, color='teal')
        ax.set_title("Количество релизов по годам", fontsize=16, pad=10)
        ax.set_xlabel("Год", fontsize=12)
        ax.set_ylabel("Количество", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Не удалось построить график: {str(e)}")

st.subheader("Распределение по рейтингам")
if not filtered_data.empty and 'rating' in filtered_data.columns:
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ratings = filtered_data['rating'].value_counts()
        ratings.plot(kind='bar', ax=ax, color='teal', edgecolor='black')
        ax.set_title("Распределение по рейтингам", fontsize=16, pad=10)
        ax.set_xlabel("Рейтинг", fontsize=12)
        ax.set_ylabel("Количество", fontsize=12)
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Не удалось построить график: {str(e)}")

st.subheader("Результаты поиска")
if not filtered_data.empty:
    st.write(f"Найдено {len(filtered_data)} записей")
    st.dataframe(filtered_data)
    
    csv = filtered_data.to_csv(index=False)
    st.download_button(
        label="Скачать отфильтрованные данные (CSV)",
        data=csv,
        file_name="netflix_filtered_data.csv",
        mime="text/csv"
    )
else:
    st.write("Нет данных, соответствующих фильтрам.")