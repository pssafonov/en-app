import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import base64
import time

st.set_page_config(page_title="English for Kids", page_icon="🇬🇧", layout="wide")

# Design with large emojis and vibrant colors
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #f0f9ff; }
    .main-title { text-align: center; color: #1e293b; font-family: 'Comic Sans MS', cursive; font-size: 45px; margin-bottom: 10px; }
    .hint { text-align: center; color: #64748b; font-size: 16px; margin-bottom: 20px; }
    
    .emoji-card {
        height: 140px;
        font-size: 70px;
        text-align: center;
        border-radius: 15px;
        background-color: white;
        border: 3px solid #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .emoji-card:hover {
        border-color: #0369a1;
        box-shadow: 0 4px 12px rgba(3, 105, 161, 0.2);
        transform: scale(1.05);
    }
    
    .emoji-card:active {
        transform: scale(0.95);
    }
    
    .letter-placeholder {
        background: linear-gradient(135deg, #0369a1 0%, #06b6d4 100%);
        color: white;
        font-family: Arial, sans-serif;
        font-weight: bold;
        font-size: 60px;
        border-radius: 15px;
    }

    .emoji-button {
        width: 100%;
        padding: 0;
        border: none;
        background: none !important;
    }
    
    .stButton>button {
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 16px;
    }
    
    .play-button {
        background-color: #10b981 !important;
        color: white !important;
        height: 50px;
        margin-bottom: 20px;
    }
    
    .play-button:hover {
        background-color: #059669 !important;
    }
    
    .next-button {
        background-color: #0369a1 !important;
        color: white !important;
        height: 50px;
        margin-top: 20px;
    }
    
    .next-button:hover {
        background-color: #0284c7 !important;
    }
    </style>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEpRq2SJhqJb0DvIx_XKwXJXCOE2h9z9tvWYdpnZNRqIIgj65FXymJnwGkavxDPo1k83wkkQtbjeAk/pub?output=csv"

@st.cache_data(ttl=5)
def load_data(url):
    df = pd.read_csv(url)
    if 'emoji' not in df.columns:
        df['emoji'] = ""
    return df

def get_display_element(word, emoji_value):
    """Returns emoji from sheet or first letter placeholder"""
    if pd.notna(emoji_value) and str(emoji_value).strip() != "":
        return str(emoji_value).strip()
    else:
        return word[0].upper()

def play_audio(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    audio_bytes = fp.getvalue()
    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
        <audio autoplay>
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
        if target_en in all_words: 
            all_words.remove(target_en)
        wrong_words = random.sample(all_words, min(len(all_words), 5))
        opts = [target_en] + wrong_words
        random.shuffle(opts)
        st.session_state.options = opts

    st.markdown("<h1 class='main-title'>Listen and Pick! 🎧</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hint'>Hint: <b>{st.session_state.current_word['ua']}</b></p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔊 TAP TO LISTEN", key="play_btn", use_container_width=True):
            play_audio(st.session_state.current_word['en'])
            st.toast("🔊 Playing...", icon="🎵")

    st.markdown("")  # Spacer

    # Display 6 options in 2 columns x 3 rows
    cols = st.columns(2, gap="medium")
    for i, option in enumerate(st.session_state.options[:6]):
        row = df[df['word'] == option].iloc[0]
        emoji_value = str(row['emoji']).strip() if pd.notna(row['emoji']) else ""
        display = get_display_element(option, emoji_value)
        is_emoji = len(display) <= 2 and ord(display[0]) > 127  # Unicode emoji check
        
        col_idx = i % 2
        with cols[col_idx]:
            if is_emoji:
                button_html = f"""
                    <button style="
                        width: 100%;
                        height: 140px;
                        font-size: 70px;
                        border: 3px solid #e2e8f0;
                        border-radius: 15px;
                        background-color: white;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        margin-bottom: 20px;
                    " onclick="document.getElementById('btn_{i}').click()">
                        {display}
                    </button>
                """
            else:
                button_html = f"""
                    <button style="
                        width: 100%;
                        height: 140px;
                        font-size: 60px;
                        border: 3px solid #e2e8f0;
                        border-radius: 15px;
                        background: linear-gradient(135deg, #0369a1 0%, #06b6d4 100%);
                        color: white;
                        font-weight: bold;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        margin-bottom: 20px;
                    " onclick="document.getElementById('btn_{i}').click()">
                        {display}
                    </button>
                """
            
            st.markdown(button_html, unsafe_allow_html=True)
            
            # Hidden button for logic
            if st.button("", key=f"btn_{i}", label_visibility="collapsed"):
                if option == st.session_state.current_word['en']:
                    st.session_state.status = "correct"
                else:
                    st.session_state.status = "wrong"
                st.rerun()

    if st.session_state.status == "correct":
        st.balloons()
        st.success("✅ CORRECT! Great job!", icon="🎉")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("NEXT ➡️", key="next_btn", use_container_width=True):
                st.session_state.current_word = None
                st.session_state.status = None
                st.rerun()
    elif st.session_state.status == "wrong":
        st.error("❌ Try again!", icon="💪")

except Exception as e:
    st.error(f"Error loading data. Check the spreadsheet! ❌\n\n{e}")
