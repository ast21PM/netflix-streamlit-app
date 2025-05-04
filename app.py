import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import sys


try:
    import matplotlib.pyplot as plt
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/netflix_titles.csv')

        if 'country' not in df.columns:
            df['country'] = 'Unknown'
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {str(e)}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("Не удалось загрузить данные. Проверьте файл data/netflix_titles.csv")
    st.stop()

st.set_page_config(page_title="Netflix Analytics", layout="wide")
st.title("📊 Netflix Content Analysis Dashboard")
st.markdown("""
Анализ каталога Netflix с использованием данных из Kaggle.
* **Источник данных:** [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)
* **Автор:** [ast_57]
""")

with st.sidebar:
    st.header("Фильтры")
    

    selected_type = st.selectbox(
        "Тип контента",
        ['All', 'Movie', 'TV Show'],
        index=0
    )
    

    min_year = df['release_year'].min() if not df.empty else 1940
    max_year = df['release_year'].max() if not df.empty else 2022
    year_range = st.slider(
        "Год выпуска",
        int(min_year), int(max_year),
        (max(int(min_year), 2010), int(max_year))
    )
    

    countries = ['All'] + sorted(df['country'].dropna().unique().tolist()) if 'country' in df.columns else ['All']
    selected_countries = st.multiselect(
        "Страны производства",
        options=countries,
        default=['All']
    )

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
            duration = filtered_data['duration'].str.extract(r'(\d+)').astype(float)
            avg_duration = duration.mean()
            st.metric("Средняя длительность", f"{avg_duration:.1f} мин" if pd.notna(avg_duration) else "N/A")
        except:
            st.metric("Средняя длительность", "N/A")
    else:
        st.metric("Средняя длительность", "N/A")

with col3:
    release_year = filtered_data['release_year'].min() if not filtered_data.empty else "N/A"
    st.metric("Самый старый релиз", release_year)

st.subheader("Распределение по рейтингам")
if not filtered_data.empty and 'rating' in filtered_data.columns:
    try:
        fig, ax = plt.subplots()
        filtered_data['rating'].value_counts().plot(kind='bar', ax=ax)
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Не удалось построить график: {str(e)}")
else:
    st.write("Нет данных для отображения графика.")


st.subheader("Таблица данных")
columns_to_show = ['title', 'type', 'release_year', 'country', 'duration']
available_columns = [col for col in columns_to_show if col in filtered_data.columns]
if available_columns:
    st.dataframe(
        filtered_data[available_columns],
        height=400,
        use_container_width=True
    )
else:
    st.warning("Нет доступных данных для отображения")


if show_stats:
    st.subheader("Дополнительная статистика")
    if not filtered_data.empty and 'country' in filtered_data.columns:
        try:
            st.write("Топ-10 стран по производству:")
            st.bar_chart(filtered_data['country'].value_counts().head(10))
        except Exception as e:
            st.warning(f"Ошибка отображения статистики: {str(e)}")
    else:
        st.write("Нет данных для отображения статистики.")