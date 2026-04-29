import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import base64

st.set_page_config(page_title="Kids English", page_icon="🇬🇧", layout="centered")

# Чистый и надежный CSS
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #fefce8; }
    
    /* Контейнер для картинки */
    .img-container {
        height: 200px;
        overflow: hidden;
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        margin-bottom: 10px;
    }
    
    .img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .main-title { text-align: center; color: #1e293b; font-family: 'Comic Sans MS', cursive; font-size: 40px; margin-bottom: 0px; }
    .hint-text { text-align: center; color: #64748b; margin-bottom: 20px; }
    
    /* Стиль кнопки выбора */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEpRq2SJhqJb0DvIx_XKwXJXCOE2h9z9tvWYdpnZNRqIIgj65FXymJnwGkavxDPo1k83wkkQtbjeAk/pub?output=csv"

@st.cache_data(ttl=10)
def load_data(url):
    return pd.read_csv(url)

def play_audio(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    audio_bytes = fp.getvalue()
    b64 = base64.b64encode(audio_bytes).decode()
    # Трюк для автоплея через HTML
    md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

if 'count' not in st.session_state:
    st.session_state.count = 0
if 'play_now' not in st.session_state:
    st.session_state.play_now = False

def next_word():
    st.session_state.count += 1
    st.session_state.play_now = False

try:
    df = load_data(SHEET_URL)
    filtered_df = df.reset_index(drop=True)

    # Выбор слова
    random.seed(st.session_state.count)
    random_idx = random.randint(0, len(filtered_df) - 1)
    target_row = filtered_df.iloc[random_idx]
    target_word = str(target_row['word']).strip()
    target_ua = str(target_row['translation']).strip()

    st.markdown(f"<h1 class='main-title'>Listen! 🎧</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hint-text'>Подсказка: {target_ua}</p>", unsafe_allow_html=True)

    # Кнопка для запуска звука (решает проблему блокировки браузером)
    col_audio, _ = st.columns([1, 3])
    with col_audio:
        if st.button("🔊 Слушать"):
            st.session_state.play_now = True

    if st.session_state.play_now:
        play_audio(target_word)

    # Готовим варианты
    all_words = df['word'].unique().tolist()
    if target_word in all_words: all_words.remove(target_word)
    wrong_words = random.sample(all_words, 2)
    options = [target_word] + wrong_words
    random.seed(st.session_state.count + 7)
    random.shuffle(options)

    # Отрисовка карточек
    cols = st.columns(3)
    for i, option in enumerate(options):
        img_url = f"https://loremflickr.com/300/300/{option.lower()}?random={st.session_state.count}_{i}"
        with cols[i]:
            # Используем HTML контейнер для картинки
            st.markdown(f'<div class="img-container"><img src="{img_url}"></div>', unsafe_allow_html=True)
            if st.button("Это?", key=f"btn_{i}_{st.session_state.count}"):
                if option == target_word:
                    st.balloons()
                    st.success("Правильно! 🎉")
                    st.button("ДАЛЬШЕ ➡️", on_click=next_word)
                else:
                    st.error("Нет ❌")

except Exception as e:
    st.error(f"Ошибка: {e}")
