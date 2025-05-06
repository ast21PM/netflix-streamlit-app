import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import sys
import os

try:
    import matplotlib.pyplot as plt
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt

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

st.set_page_config(page_title="Netflix Analytics", layout="wide")
st.title("📊 Анализ контента Netflix")
st.markdown("""
Анализ каталога Netflix с использованием данных из Kaggle.
* Источник данных: [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)
* Автор: [ast_57]
""")

with st.sidebar:
    st.header("Фильтры")

    min_year = 1940
    max_year = 2022
    
    if not df.empty:
        min_year = int(df['release_year'].min()) if 'release_year' in df.columns else 1940
        max_year = int(df['release_year'].max()) if 'release_year' in df.columns else 2022

    year_range = st.slider(
        "Год выпуска",
        min_year, max_year,
        (max(min_year, 2010), max_year)
    )
    
    countries = ['All'] + sorted(df['country'].dropna().unique().tolist()) if 'country' in df.columns else ['All']
    selected_countries = st.multiselect(
        "Страны производства",
        options=countries,
        default=['All']
    )

    selected_type = st.selectbox("Тип контента", options=['All', 'Movie', 'TV Show'])
    
    show_stats = st.checkbox("Показать статистику")
    search_query = st.text_input("Поиск по названию")


try:
    filtered_data = df.copy()
    

    if selected_type != 'All' and 'type' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['type'] == selected_type]
    

    if 'release_year' in filtered_data.columns:
        filtered_data = filtered_data[
            filtered_data['release_year'].between(year_range[0], year_range[1])
        ]
    else:
        st.warning("Столбец 'release_year' отсутствует, фильтр по году не применен.")
    

    if 'All' not in selected_countries and 'country' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['country'].isin(selected_countries)]
    

    if search_query:
        if 'title' in filtered_data.columns:
            try:
                filtered_data = filtered_data[
                    filtered_data['title'].str.contains(search_query, case=False, na=False)
                ]
            except Exception as e:
                st.error(f"Ошибка при поиске: {str(e)}")
        else:
            st.warning("Столбец 'title' отсутствует в датасете. Поиск невозможен.")
    else:
        st.info("Введите запрос для поиска по названию.")

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
        except Exception as e:
            st.metric("Средняя длительность", "N/A")
            st.warning(f"Ошибка при расчете средней длительности: {str(e)}")
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
        ax.set_title("Распределение по рейтингам")
        ax.set_xlabel("Рейтинг")
        ax.set_ylabel("Количество")
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Не удалось построить график: {str(e)}")
else:
    st.write("Нет данных для отображения графика.")


st.subheader("Результаты поиска")
if not filtered_data.empty:
    st.write(f"Найдено {len(filtered_data)} записей")
    st.dataframe(filtered_data)
else:
    st.write("Нет данных, соответствующих фильтрам.")