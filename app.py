import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="English for Kids", page_icon="🇬🇧", layout="centered")

# Стили для удобства ребенка
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 80px; font-size: 24px; border-radius: 20px; font-weight: bold; }
    .word-box { background-color: #f0f9ff; padding: 30px; border-radius: 25px; text-align: center; border: 3px solid #0369a1; margin-bottom: 20px; }
    h1 { color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# ВАША ССЫЛКА УЖЕ ЗДЕСЬ
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEpRq2SJhqJb0DvIx_XKwXJXCOE2h9z9tvWYdpnZNRqIIgj65FXymJnwGkavxDPo1k83wkkQtbjeAk/pub?output=csv"

@st.cache_data(ttl=10) # Уменьшил время кэша до 10 секунд для быстрой синхронизации
def load_data(url):
    return pd.read_csv(url)

def get_audio(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

# Инициализация состояний
if 'count' not in st.session_state:
    st.session_state.count = 0

def next_word():
    st.session_state.count += 1

try:
    df = load_data(SHEET_URL)
    
    # Боковая панель
    st.sidebar.title("Settings")
    categories = ["All Topics"] + sorted(list(df['category'].dropna().unique()))
    selected_cat = st.sidebar.selectbox("Choose a topic:", categories)
    
    if selected_cat != "All Topics":
        filtered_df = df[df['category'] == selected_cat].reset_index(drop=True)
    else:
        filtered_df = df.reset_index(drop=True)

    # Выбираем слово на основе счетчика (используем random.seed, чтобы слово было стабильным до нажатия кнопки)
    random.seed(st.session_state.count)
    random_idx = random.randint(0, len(filtered_df) - 1)
    current_row = filtered_df.iloc[random_idx]
    
    word = str(current_row['word']).strip()
    translation = str(current_row['translation']).strip()

    st.title("🌈 Fun English Time!")

    # 1. Картинка (используем Unsplash для более качественных фото)
    img_url = f"https://source.unsplash.com/featured/800x600/?{word.lower()}"
    # Если Unsplash тормозит, используем проверенный loremflickr
    backup_img_url = f"https://loremflickr.com/800/600/{word.lower()}"
    st.image(backup_img_url, use_container_width=True)

    # 2. Слово на украинском
    st.markdown(f"<div class='word-box'><h1>{translation}</h1></div>", unsafe_allow_html=True)

    # 3. Озвучка
    audio_data = get_audio(word)
    if audio_data:
        st.audio(audio_data, format="audio/mp3")

    # 4. Варианты ответов
    all_words = df['word'].unique().tolist()
    if word in all_words: all_words.remove(word)
    wrong_options = random.sample(all_words, min(len(all_words), 2))
    
    options = [word] + wrong_options
    random.seed(st.session_state.count + 42) # Другой сид для перемешивания кнопок
    random.shuffle(options)

    st.write("### Pick the right word:")
    cols = st.columns(3)
    
    for i, option in enumerate(options):
        if cols[i].button(option, key=f"btn_{i}_{st.session_state.count}"):
            if option == word:
                st.balloons()
                st.success(f"Excellent! It's {word}! 🎉")
                st.button("NEXT WORD ➡️", on_click=next_word, type="primary")
            else:
                st.error("Not quite! Try again! 💪")

    if st.sidebar.button("Skip Word ➡️"):
        next_word()
        st.rerun()

except Exception as e:
    st.error(f"Waiting for data... or Error: {e}")
