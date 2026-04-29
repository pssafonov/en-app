import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import base64

st.set_page_config(page_title="English for Kids", page_icon="🇬🇧", layout="centered")

# Ваш любимый визуальный стиль
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #f0f9ff; }
    .main-title { text-align: center; color: #1e293b; font-family: 'Comic Sans MS', cursive; font-size: 45px; margin-bottom:0; }
    .hint { text-align: center; color: #64748b; font-size: 18px; margin-bottom: 10px; }
    
    /* Контейнер для картинки, чтобы они были одинаковыми */
    .img-card {
        height: 200px;
        border-radius: 20px 20px 0 0;
        overflow: hidden;
        border: 4px solid #fff;
        background-color: white;
    }
    .img-card img {
        width: 100%;
        height: 100%;
        object-fit: contain; /* Картинка видна полностью */
    }
    
    /* Кнопка под картинкой */
    .stButton>button {
        border-radius: 0 0 20px 20px !important;
        border: none !important;
        background-color: #ffffff !important;
        color: #0369a1 !important;
        font-weight: bold !important;
        height: 50px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stButton>button:hover {
        background-color: #0369a1 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEpRq2SJhqJb0DvIx_XKwXJXCOE2h9z9tvWYdpnZNRqIIgj65FXymJnwGkavxDPo1k83wkkQtbjeAk/pub?output=csv"

@st.cache_data(ttl=5)
def load_data(url):
    return pd.read_csv(url)

def play_audio(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    audio_bytes = fp.getvalue()
    b64 = base64.b64encode(audio_bytes).decode()
    md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

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
        wrong_words = random.sample(all_words, 2)
        opts = [target_en] + wrong_words
        random.shuffle(opts)
        st.session_state.options = opts

    target_word = st.session_state.current_word['en']
    target_ua = st.session_state.current_word['ua']

    st.markdown(f"<h1 class='main-title'>Listen! 🎧</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hint'>Підказка для тата: <b>{target_ua}</b></p>", unsafe_allow_html=True)

    if st.button("🔊 PLAY SOUND", type="primary", use_container_width=True):
        play_audio(target_word)

    # Отрисовка карточек
    cols = st.columns(3)
    for i, option in enumerate(st.session_state.options):
        # Используем loremflickr, но через стандартный st.image
        img_url = f"https://loremflickr.com/400/400/{option.lower().replace(' ', ',')}?random={st.session_state.current_word['en']}_{i}"
        
        with cols[i]:
            # Сама карточка
            st.markdown(f'<div class="img-card"><img src="{img_url}"></div>', unsafe_allow_html=True)
            # Кнопка выбора
            if st.button("Pick me!", key=f"btn_{i}"):
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
