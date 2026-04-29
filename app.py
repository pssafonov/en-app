import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import base64
import time

st.set_page_config(page_title="English for Kids", page_icon="🇬🇧", layout="centered")

# Финальный дизайн: огромные эмодзи и сочные цвета
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #f0f9ff; }
    .main-title { text-align: center; color: #1e293b; font-family: 'Comic Sans MS', cursive; font-size: 45px; margin-bottom:0; }
    .hint { text-align: center; color: #64748b; font-size: 18px; margin-bottom: 10px; }
    
    .emoji-card {
        height: 200px;
        font-size: 100px;
        text-align: center;
        border-radius: 20px 20px 0 0;
        background-color: white;
        border: 4px solid #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Стиль для букв-заглушек, если нет эмодзи */
    .letter-placeholder {
        background-color: #e2e8f0;
        color: #475569;
        font-family: sans-serif;
        font-weight: bold;
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

@st.cache_data(ttl=5)
def load_data(url):
    df = pd.read_csv(url)
    # Если колонки emoji нет, создаем пустую
    if 'emoji' not in df.columns:
        df['emoji'] = ""
    return df

def play_audio(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    audio_bytes = fp.getvalue()
    b64 = base64.b64encode(audio_bytes).decode()
    # Уникальный ключ для аудио, чтобы обмануть кэш браузера
    audio_html = f"""
        <audio autoplay key="{time.time()}">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

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
            'ua': str(target_row['translation']).strip(),
            'emoji': str(target_row['emoji']).strip() if pd.notna(target_row['emoji']) else ""
        }
        all_words = df['word'].unique().tolist()
        target_en = st.session_state.current_word['en']
        if target_en in all_words: all_words.remove(target_en)
        wrong_words = random.sample(all_words, min(len(all_words), 2))
        opts = [target_en] + wrong_words
        random.shuffle(opts)
        st.session_state.options = opts

    st.markdown("<h1 class='main-title'>Listen and Pick! 🎧</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hint'>Подсказка для папы: <b>{st.session_state.current_word['ua']}</b></p>", unsafe_allow_html=True)

    if st.button("🔊 СЛУШАТЬ СЛОВО (PLAY)", type="primary", use_container_width=True):
        play_audio(st.session_state.current_word['en'])

    cols = st.columns(3)
    for i, option in enumerate(st.session_state.options):
        # Ищем эмодзи для варианта
        row = df[df['word'] == option].iloc[0]
        emoji = str(row['emoji']).strip() if pd.notna(row['emoji']) and str(row['emoji']).strip() != "" else ""
        
        with cols[i]:
            if emoji:
                st.markdown(f'<div class="emoji-card">{emoji}</div>', unsafe_allow_html=True)
            else:
                # Если эмодзи нет — рисуем букву
                letter = option[0].upper()
                st.markdown(f'<div class="emoji-card letter-placeholder">{letter}</div>', unsafe_allow_html=True)
            
            if st.button("Это?", key=f"btn_{i}"):
                if option == st.session_state.current_word['en']:
                    st.session_state.status = "correct"
                else:
                    st.session_state.status = "wrong"

    if st.session_state.status == "correct":
        st.balloons()
        st.success("ПРАВИЛЬНО! 🎉")
        if st.button("СЛЕДУЮЩЕЕ ➡️", use_container_width=True, type="primary"):
            st.session_state.current_word = None
            st.session_state.status = None
            st.rerun()
    elif st.session_state.status == "wrong":
        st.error("Попробуй еще раз! ❌")

except Exception as e:
    st.error(f"Обновите таблицу! Ошибка: {e}")
