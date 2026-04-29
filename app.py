import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="English for Kids", page_icon="🇬🇧")

# Стили для красивых кнопок
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px;
    }
    </style>
    """, unsafe_allow_status_code=True)

st.title("🌟 My English Learning App")

# Ссылка на вашу таблицу (замените на свою ссылку CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEpRq2SJhqJb0DvIx_XKwXJXCOE2h9z9tvWYdpnZNRqIIgj65FXymJnwGkavxDPo1k83wkkQtbjeAk/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(sheet_url)
    
    # 1. Выбор темы (Interface in English)
    categories = ["All Topics"] + list(df['category'].unique())
    selected_cat = st.sidebar.selectbox("Choose a topic:", categories)

    if selected_cat != "All Topics":
        filtered_df = df[df['category'] == selected_cat]
    else:
        filtered_df = df

    # Логика выбора слова
    if 'current_word_idx' not in st.session_state or st.session_state.get('reset_word'):
        st.session_state.current_word_idx = random.choice(filtered_df.index)
        st.session_state.reset_word = False

    current_row = df.loc[st.session_state.current_word_idx]
    word = current_row['word']
    translation = current_row['translation']

    st.write(f"### How do you say in English:")
    st.info(f"## {translation}")

    # Озвучка
    audio_html = f"""
        <audio controls autoplay key="{word}">
          <source src="https://translate.google.com/translate_tts?ie=UTF-8&q={word}&tl=en&client=tw-ob" type="audio/mpeg">
        </audio>
    """
    st.components.v1.html(audio_html, height=100)

    # Варианты ответов (один правильный + два случайных)
    other_words = df[df['word'] != word]['word'].sample(2).tolist()
    options = [word] + other_words
    random.shuffle(options)

    # Кнопки выбора
    cols = st.columns(3)
    for i, option in enumerate(options):
        if cols[i].button(option):
            if option == word:
                st.balloons()
                st.success(f"Yes! It's {word}! 🎉")
                if st.button("Next Word ➡️"):
                    st.session_state.reset_word = True
                    st.rerun()
            else:
                st.error("Try again! 💪")

except Exception as e:
    st.warning("Please check your Google Sheet link or columns (word, translation, category).")
