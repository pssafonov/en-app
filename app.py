import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import base64
from st_clickable_images import clickable_images

st.set_page_config(page_title="English for Kids", page_icon="🇬🇧", layout="centered")

# Наводим красоту
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #f0f9ff; }
    .main-title { text-align: center; color: #1e293b; font-family: 'Comic Sans MS', cursive; font-size: 45px; }
    .hint { text-align: center; color: #64748b; font-size: 18px; margin-bottom: 10px; }
    /* Центрируем блок с картинками */
    div[style*="flex-direction: column;"] { align-items: center; }
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
    md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

if 'count' not in st.session_state:
    st.session_state.count = 0
if 'status' not in st.session_state:
    st.session_state.status = None

try:
    df = load_data(SHEET_URL)
    
    # Выбор слова
    random.seed(st.session_state.count)
    random_idx = random.randint(0, len(df) - 1)
    target_word = str(df.iloc[random_idx]['word']).strip()
    target_ua = str(df.iloc[random_idx]['translation']).strip()

    st.markdown(f"<h1 class='main-title'>Listen! 🎧</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hint'>Підказка для тата: <b>{target_ua}</b></p>", unsafe_allow_html=True)

    # Кнопка звука
    if st.button("🔊 PLAY SOUND", type="primary", use_container_width=True):
        play_audio(target_word)

    # Готовим варианты
    all_words = df['word'].unique().tolist()
    if target_word in all_words: all_words.remove(target_word)
    wrong_words = random.sample(all_words, 2)
    options = [target_word] + wrong_words
    random.seed(st.session_state.count + 7)
    random.shuffle(options)

    # Собираем список URL для картинок
    # Используем Unsplash Source для более предсказуемых результатов
    images_urls = [f"https://images.unsplash.com/photo-1?w=400&h=400&fit=crop&q=80&{opt}" 
                   if "http" not in opt else opt for opt in options]
    
    # Чтобы Unsplash находил именно то, что нужно:
    images_urls = [f"https://loremflickr.com/400/400/{opt.lower()}?random={st.session_state.count}_{i}" for i, opt in enumerate(options)]

    # Отображаем картинки как кнопки
    clicked = clickable_images(
        images_urls,
        titles=[f"Option {i}" for i in range(len(options))],
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap", "gap": "20px"},
        img_style={"margin": "10px", "width": "250px", "height": "250px", "border-radius": "20px", "border": "5px solid #fff", "object-fit": "contain", "background": "white", "cursor": "pointer"},
    )

    # Обработка нажатия
    if clicked > -1:
        selected_word = options[clicked]
        if selected_word == target_word:
            st.session_state.status = "correct"
        else:
            st.session_state.status = "wrong"

    # Вывод результата
    if st.session_state.status == "correct":
        st.balloons()
        st.success(f"YES! It's {target_word}! 🎉")
        if st.button("NEXT WORD ➡️", use_container_width=True):
            st.session_state.count += 1
            st.session_state.status = None
            st.rerun()
    elif st.session_state.status == "wrong":
        st.error("Try again! ❌")

except Exception as e:
    st.error(f"Waiting for data... {e}")
