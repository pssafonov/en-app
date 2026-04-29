import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="English Kids Game", page_icon="🇬🇧", layout="centered")

# Мощный CSS для создания красивых и одинаковых карточек
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #fefce8; }
    
    /* Сетка для карточек */
    .cards-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-top: 30px;
    }

    /* Стили для кнопки-карточки */
    .stButton>button {
        padding: 0 !important;
        border-radius: 20px !important;
        border: 4px solid #e2e8f0 !important;
        background-color: white !important;
        transition: 0.3s !important;
        height: 320px !important; /* Фиксированная высота всей карточки */
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        overflow: hidden !important;
    }

    /* Эффект при наведении */
    .stButton>button:hover {
        border: 4px solid #facc15 !important;
        transform: scale(1.03);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }

    /* Стиль для картинки внутри кнопки */
    .card-img {
        width: 100%;
        height: 250px; /* Фиксированная высота картинки */
        object-fit: cover; /* Картинка обрезается, чтобы заполнить квадрат */
    }

    /* Стиль для текста под картинкой */
    .card-text {
        font-size: 22px;
        font-weight: bold;
        color: #1e293b;
        margin-top: 15px;
        font-family: 'Comic Sans MS', cursive;
    }
    
    .main-title { text-align: center; color: #1e293b; font-family: 'Comic Sans MS', cursive; margin-bottom: 0;}
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
    
    # Боковая панель (оставляем без изменений)
    st.sidebar.title("Settings")
    categories = ["All Topics"] + sorted(list(df['category'].dropna().unique()))
    selected_cat = st.sidebar.selectbox("Choose a topic:", categories)
    
    filtered_df = df if selected_cat == "All Topics" else df[df['category'] == selected_cat]
    filtered_df = filtered_df.reset_index(drop=True)

    # Выбор слова
    random.seed(st.session_state.count)
    random_idx = random.randint(0, len(filtered_df) - 1)
    target_row = filtered_df.iloc[random_idx]
    target_word = str(target_row['word']).strip()
    target_ua = str(target_row['translation']).strip()

    st.markdown("<h1 class='main-title'>Listen and Pick! 🎧</h1>", unsafe_allow_html=True)
    st.write(f"<p style='text-align:center; color:#64748b;'>Hint for Dad: {target_ua}</p>", unsafe_allow_html=True)
    
    # Плеер
    audio_data = get_audio(target_word)
    if audio_data:
        st.audio(audio_data, format="audio/mp3")

    # Готовим 3 варианта
    all_words = df['word'].unique().tolist()
    if target_word in all_words: all_words.remove(target_word)
    wrong_words = random.sample(all_words, 2)
    
    options = [target_word] + wrong_words
    random.seed(st.session_state.count + 7)
    random.shuffle(options)

    # ОТОБРАЖАЕМ КАРТОЧКИ (HTML + CSS внутри кнопок Streamlit)
    # Используем проверенный источник картинок
    
    cols = st.columns(3)
    for i, option in enumerate(options):
        # Генерируем ссылку. random_idx нужен, чтобы картинки были разными
        img_url = f"https://loremflickr.com/400/400/{option.lower()}?random={st.session_state.count}_{i}"
        
        # HTML код, который будет лежать внутри кнопки
        button_content = f"""
            <img src="{img_url}" class="card-img">
            <div class="card-text">Pick me!</div>
        """
        
        with cols[i]:
            # Ключевой момент: мы кладем HTML внутрь label кнопки
            if st.button(button_content, key=f"btn_{i}_{st.session_state.count}", unsafe_allow_html=True):
                if option == target_word:
                    st.balloons()
                    st.success(f"YES! 🎉")
                    st.button("NEXT ➡️", on_click=next_word, type="primary")
                else:
                    st.error("Try again! ❌")

except Exception as e:
    st.error(f"Error: {e}")
