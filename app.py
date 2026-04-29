import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="English for Kids", page_icon="🇬🇧", layout="centered")

# Настройка стилей
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 70px; font-size: 24px; border-radius: 15px; background-color: #f0f2f6; }
    .stButton>button:hover { background-color: #e0e2e6; border: 2px solid #0369a1; }
    .word-box { background-color: #e0f2fe; padding: 20px; border-radius: 20px; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Ссылка на вашу таблицу (CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEpRq2SJhqJb0DvIx_XKwXJXCOE2h9z9tvWYdpnZNRqIIgj65FXymJnwGkavxDPo1k83wkkQtbjeAk/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url)

def get_audio(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

try:
    df = load_data(sheet_url)
    
    # Выбор категории в боковой панели
    categories = ["All Topics"] + list(df['category'].unique())
    selected_cat = st.sidebar.selectbox("Choose a topic:", categories)
    
    filtered_df = df if selected_cat == "All Topics" else df[df['category'] == selected_cat]

    # Инициализация индекса слова в памяти приложения
    if 'current_idx' not in st.session_state or st.session_state.get('refresh'):
        st.session_state.current_idx = random.choice(filtered_df.index)
        st.session_state.refresh = False

    current_row = df.loc[st.session_state.current_idx]
    word = current_row['word']
    translation = current_row['translation']

    # ИНТЕРФЕЙС
    st.title("🐾 Learning is Fun!")
    
    # 1. Автоматическая картинка
    image_url = f"https://loremflickr.com/400/300/{word.lower()}"
    st.image(image_url, caption=f"Look at this!", use_container_width=True)

    # 2. Задание
    st.markdown(f"<div class='word-box'><h1>{translation}</h1></div>", unsafe_allow_html=True)

    # 3. Звук (автоматически при загрузке слова)
    audio_data = get_audio(word)
    st.audio(audio_data, format="audio/mp3")

    # 4. Варианты ответов
    all_en_words = df['word'].unique().tolist()
    if word in all_en_words: all_en_words.remove(word)
    
    wrong_options = random.sample(all_en_words, min(len(all_en_words), 2))
    options = [word] + wrong_options
    random.shuffle(options)

    cols = st.columns(3)
    for i, option in enumerate(options):
        if cols[i].button(option):
            if option == word:
                st.balloons()
                st.success("🎉 CORRECT! Well done!")
                if st.button("NEXT WORD ➡️", type="primary"):
                    st.session_state.refresh = True
                    st.rerun()
            else:
                st.error("Oops! Try again! 💪")

    if st.sidebar.button("Skip / Random Word 🔀"):
        st.session_state.refresh = True
        st.rerun()

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Check your Google Sheet link and 'word', 'translation', 'category' columns.")
