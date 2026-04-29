import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import base64
from st_clickable_images import clickable_images

st.set_page_config(page_title="English for Kids", page_icon="🇬🇧", layout="centered")

# Сохраняем твой любимый визуальный стиль
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #f0f9ff; }
    .main-title { text-align: center; color: #1e293b; font-family: 'Comic Sans MS', cursive; font-size: 45px; }
    .hint { text-align: center; color: #64748b; font-size: 18px; margin-bottom: 10px; }
    div[style*="flex-direction: column;"] { align-items: center; }
    </style>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEpRq2SJhqJb0DvIx_XKwXJXCOE2h9z9tvWYdpnZNRqIIgj65FXymJnwGkavxDPo1k83wkkQtbjeAk/pub?output=csv"

@st.cache_data(ttl=5) # Обновляем данные чаще
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
    
    # Логика выбора нового слова (срабатывает в начале или при нажатии NEXT)
    if st.session_state.current_word is None:
        target_row = df.sample(n=1).iloc[0]
        st.session_state.current_word = {
            'en': str(target_row['word']).strip(),
            'ua': str(target_row['translation']).strip()
        }
        # Подбираем варианты
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

    # Собираем ссылки на картинки (используем стабильный источник)
    images_urls = [
        f"https://loremflickr.com/400/400/{opt.lower().replace(' ', ',')}?lock={i+10}" 
        for i, opt in enumerate(st.session_state.options)
    ]

    # Кликабельные изображения
    clicked = clickable_images(
        images_urls,
        titles=st.session_state.options,
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap", "gap": "20px"},
        img_style={"margin": "5px", "width": "200px", "height": "200px", "border-radius": "20px", "border": "5px solid #fff", "object-fit": "cover", "background": "white", "cursor": "pointer"},
    )

    # Если нажали на картинку
    if clicked > -1:
        selected_word = st.session_state.options[clicked]
        if selected_word == target_word:
            st.session_state.status = "correct"
        else:
            st.session_state.status = "wrong"

    # Реакция на ответ
    if st.session_state.status == "correct":
        st.balloons()
        st.success(f"YES! 🎉 It's {target_word}")
        if st.button("NEXT WORD ➡️", use_container_width=True, type="primary"):
            st.session_state.current_word = None # Сброс для выбора нового слова
            st.session_state.status = None
            st.rerun()
    elif st.session_state.status == "wrong":
        st.error("Try again! ❌")

except Exception as e:
    st.error(f"Waiting for data or error: {e}")
