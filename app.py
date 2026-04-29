import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="English for Kids", page_icon="🇬🇧", layout="centered")

# Яркие стили для ребенка
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #fefce8; }
    .stButton>button { border-radius: 20px; border: 4px solid #e2e8f0; transition: 0.3s; height: 250px; }
    .stButton>button:hover { border: 4px solid #facc15; transform: scale(1.02); }
    .main-title { text-align: center; color: #1e293b; font-family: 'Comic Sans MS', cursive; }
    </style>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEpRq2SJhqJb0DvIx_XKwXJXCOE2h9z9tvWYdpnZNRqIIgj65FXymJnwGkavxDPo1k83wkkQtbjeAk/pub?output=csv"

@st.cache_data(ttl=10)
def load_data(url):
    return pd.read_csv(url)

def get_audio(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except: return None

if 'count' not in st.session_state:
    st.session_state.count = 0

def next_word():
    st.session_state.count += 1

try:
    df = load_data(SHEET_URL)
    categories = ["All Topics"] + sorted(list(df['category'].dropna().unique()))
    selected_cat = st.sidebar.selectbox("Choose a topic:", categories)
    
    filtered_df = df if selected_cat == "All Topics" else df[df['category'] == selected_cat]
    filtered_df = filtered_df.reset_index(drop=True)

    # Выбор основного слова
    random.seed(st.session_state.count)
    random_idx = random.randint(0, len(filtered_df) - 1)
    target_row = filtered_df.iloc[random_idx]
    target_word = str(target_row['word']).strip()
    target_ua = str(target_row['translation']).strip()

    st.markdown("<h1 class='main-title'>Listen and Pick! 🎧</h1>", unsafe_allow_html=True)
    
    # Авто-произношение задания
    audio_data = get_audio(target_word)
    if audio_data:
        st.audio(audio_data, format="audio/mp3")
    
    st.write(f"### Подсказка (для папы): {target_ua}")

    # Готовим 3 варианта (картинки)
    all_words = df['word'].unique().tolist()
    if target_word in all_words: all_words.remove(target_word)
    wrong_words = random.sample(all_words, 2)
    
    options = [target_word] + wrong_words
    random.seed(st.session_state.count + 7)
    random.shuffle(options)

    # Отображаем картинки как кнопки
    cols = st.columns(3)
    for i, option in enumerate(options):
        # Генерируем ссылку на картинку для каждого варианта
        img_url = f"https://loremflickr.com/400/400/{option.lower()}?random={i}"
        
        with cols[i]:
            st.image(img_url, use_container_width=True)
            if st.button(f"Pick me! #{i}", key=f"btn_{i}_{st.session_state.count}"):
                if option == target_word:
                    st.balloons()
                    st.success(f"YES! It's {target_word}! 🎉")
                    st.button("NEXT ➡️", on_click=next_word, type="primary")
                else:
                    st.error("Try another one! ❌")

    if st.sidebar.button("Skip Word ➡️"):
        next_word()
        st.rerun()

except Exception as e:
    st.error(f"Error: {e}")
