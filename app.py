import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="English Kids Game", page_icon="🇬🇧", layout="centered")

# Чиним интерфейс через CSS (без хаков в кнопках)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #fefce8; }
    
    /* Фиксируем высоту контейнера с картинкой, чтобы кнопки не прыгали */
    [data-testid="stVerticalBlock"] > div:has(img) {
        height: 250px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 15px;
        background-color: white;
        border: 2px solid #e2e8f0;
    }
    
    img {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Обрезает картинку ровно под квадрат */
    }

    /* Стилизуем кнопки под картинками */
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        background-color: #ffffff !important;
        border: 3px solid #0369a1 !important;
        color: #0369a1 !important;
    }
    
    .stButton>button:hover {
        background-color: #0369a1 !important;
        color: white !important;
    }

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

    random.seed(st.session_state.count)
    random_idx = random.randint(0, len(filtered_df) - 1)
    target_row = filtered_df.iloc[random_idx]
    target_word = str(target_row['word']).strip()
    target_ua = str(target_row['translation']).strip()

    st.markdown("<h1 class='main-title'>Listen and Pick! 🎧</h1>", unsafe_allow_html=True)
    st.write(f"<p style='text-align:center; color:#64748b;'>Hint: {target_ua}</p>", unsafe_allow_html=True)
    
    audio_data = get_audio(target_word)
    if audio_data:
        st.audio(audio_data, format="audio/mp3")

    all_words = df['word'].unique().tolist()
    if target_word in all_words: all_words.remove(target_word)
    wrong_words = random.sample(all_words, 2)
    
    options = [target_word] + wrong_words
    random.seed(st.session_state.count + 7)
    random.shuffle(options)

    # Рисуем колонки
    cols = st.columns(3)
    for i, option in enumerate(options):
        # Генерируем ссылку на картинку
        img_url = f"https://loremflickr.com/400/400/{option.lower()}?random={st.session_state.count}_{i}"
        
        with cols[i]:
            st.image(img_url) # Картинка сверху
            # Кнопка строго под картинкой
            if st.button(f"Choose", key=f"btn_{i}_{st.session_state.count}"):
                if option == target_word:
                    st.balloons()
                    st.success("YES! 🎉")
                    st.button("NEXT ➡️", on_click=next_word, type="primary")
                else:
                    st.error("Try again! ❌")

except Exception as e:
    st.error(f"Something went wrong: {e}")
