import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import base64
import requests

st.set_page_config(page_title="English for Kids", page_icon="🇬🇧", layout="centered")

# Сохраняем твой макет и цвета
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #f0f9ff; }
    .main-title { text-align: center; color: #1e293b; font-family: 'Comic Sans MS', cursive; font-size: 45px; margin-bottom:0; }
    .hint { text-align: center; color: #64748b; font-size: 18px; margin-bottom: 10px; }
    
    .img-card {
        height: 220px;
        border-radius: 20px 20px 0 0;
        overflow: hidden;
        border: 4px solid #fff;
        background-color: white;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .img-card img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }
    
    .stButton>button {
        border-radius: 0 0 20px 20px !important;
        border: none !important;
        background-color: #ffffff !important;
        color: #0369a1 !important;
        font-weight: bold !important;
        height: 50px;
        font-size: 18px;
    }
    .stButton>button:hover {
        background-color: #0369a1 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEpRq2SJhqJb0DvIx_XKwXJXCOE2h9z9tvWYdpnZNRqIIgj65FXymJnwGkavxDPo1k83wkkQtbjeAk/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url)

# Функция поиска качественной картинки (Бесплатно)
@st.cache_data(show_spinner=False)
def get_safe_image(word):
    # Поиск по открытой базе Pixabay (без ключа через их редирект или аналоги)
    # Для стабильности используем проверенный лоадер с фильтром "картинка для детей"
    return f"https://loremflickr.com/400/400/{word},cartoon,whitebackground/all"

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        audio_bytes = fp.getvalue()
        b64 = base64.b64encode(audio_bytes).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    except:
        st.warning("Звук временно недоступен")

# Инициализация состояний
if 'current_word' not in st.session_state:
    st.session_state.current_word = None
if 'options' not in st.session_state:
    st.session_state.options = []
if 'status' not in st.session_state:
    st.session_state.status = None

try:
    df = load_data(SHEET_URL)
    
    if st.session_state.current_word is None:
        target_row = df.sample(n=1).iloc[0]
        st.session_state.current_word = {
            'en': str(target_row['word']).strip(),
            'ua': str(target_row['translation']).strip()
        }
        all_words = df['word'].unique().tolist()
        target_en = st.session_state.current_word['en']
        if target_en in all_words: all_words.remove(target_en)
        wrong_words = random.sample(all_words, min(len(all_words), 2))
        opts = [target_en] + wrong_words
        random.shuffle(opts)
        st.session_state.options = opts

    target_word = st.session_state.current_word['en']
    target_ua = st.session_state.current_word['ua']

    st.markdown(f"<h1 class='main-title'>Listen! 🎧</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hint'>Підказка: <b>{target_ua}</b></p>", unsafe_allow_html=True)

    if st.button("🔊 PLAY SOUND", type="primary", use_container_width=True):
        play_audio(target_word)

    # Отрисовка карточек
    cols = st.columns(3)
    for i, option in enumerate(st.session_state.options):
        # Добавляем к запросу "cartoon", чтобы картинки были более детскими и понятными
        img_url = get_safe_image(option)
        
        with cols[i]:
            st.markdown(f'<div class="img-card"><img src="{img_url}"></div>', unsafe_allow_html=True)
            if st.button("Pick!", key=f"btn_{i}"):
                if option == target_word:
                    st.session_state.status = "correct"
                else:
                    st.session_state.status = "wrong"

    if st.session_state.status == "correct":
        st.balloons()
        st.success(f"YES! 🎉 It's {target_word}")
        if st.button("NEXT WORD ➡️", use_container_width=True, type="primary"):
            st.session_state.current_word = None
            st.session_state.status = None
            st.rerun()
    elif st.session_state.status == "wrong":
        st.error("Try again! ❌")

except Exception as e:
    st.error(f"Waiting for data... {e}")
