import logging
from typing import Tuple

import firebase_auth_functions
import streamlit as st
import util
from audiorecorder import audiorecorder
from OpenAIClient import OpenAIClient
from PIL import Image
from streamlit_oauth import OAuth2Component


def init_homepage() -> Tuple[st.selectbox, st.selectbox]:
  """Initialize the Chatbox and the Sidebar of streamlit.
  
  Initialize the session state and the sidebar.

  Returns:
    A tuple cotaining the two selectbox of chat model and tts voice.
  """
  st.title("Chatbox")

  if "messages" not in st.session_state:
     st.session_state.messages = []

  with st.sidebar:
    st.markdown("""
      <style >
      .stDownloadButton, div.stButton {text-align:center}
      .stDownloadButton button, div.stButton > button:first-child {
          background-color: #48cae4;
          color:#000000;
          border-radius: 2px;
          border: 2px solid #48cae4;                                                   
      }
          }
      </style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    #set three colums on the page, markdown on the 2nd col to ensure center positioning.
    with col1:
        st.write(' ')

    with col2:
        st.markdown("<h1 style='text-align: center;color: #03045e'>Ecco6</h1>", unsafe_allow_html=True)
        image = Image.open('./ecco6/Ecco6-Logo-example.png')
        st.image(image, width=90)

    with col3:
        st.write(' ')

    st.info("This app is a voice AI assistant, which is able to connect to multiple services.")
    st.button(label='Sign Out', on_click=firebase_auth_functions.sign_out, type='primary')

    settings_expander = st.expander(label='Settings')
    with settings_expander:
      openai_chat_model = st.selectbox(
        "OpenAI chat model",
        ("gpt-4-turbo", "gpt-3.5-turbo")
      )
      openai_tts_voice = st.selectbox(
        "OpenAI voice options",
        ("alloy", "echo", "fable", "onyx", "nova", "shimmer")
      )

    settings_expander = st.expander(label='Services')
    with settings_expander:
      st.write("Services to Google:")
      authorization_url = st.secrets["AUTHORIZATION_URL"]
      token_url = st.secrets["TOKEN_URL"]
      revoke_url = st.secrets["REDIRECT_URI"][0]
      client_id = st.secrets["CLIENT_ID"]
      client_secret = st.secrets["CLIENT_SECRET"]
      redirect_uri = st.secrets["REDIRECT_URI"][0]
      scopes = "https://www.googleapis.com/auth/calendar https://mail.google.com/"
      oauth2 = OAuth2Component(
        client_id, client_secret, authorization_url, token_url, token_url, revoke_url)
      if 'google_token' not in st.session_state:
        result = oauth2.authorize_button(
          "Continue with Google", redirect_uri, scopes,
          icon="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 48 48'%3E%3Cdefs%3E%3Cpath id='a' d='M44.5 20H24v8.5h11.8C34.7 33.9 30.1 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 4.1 29.6 2 24 2 11.8 2 2 11.8 2 24s9.8 22 22 22c11 0 21-8 21-22 0-1.3-.2-2.7-.5-4z'/%3E%3C/defs%3E%3CclipPath id='b'%3E%3Cuse xlink:href='%23a' overflow='visible'/%3E%3C/clipPath%3E%3Cpath clip-path='url(%23b)' fill='%23FBBC05' d='M0 37V11l17 13z'/%3E%3Cpath clip-path='url(%23b)' fill='%23EA4335' d='M0 11l17 13 7-6.1L48 14V0H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%2334A853' d='M0 37l30-23 7.9 1L48 0v48H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%234285F4' d='M48 48L17 24l-4-3 35-10z'/%3E%3C/svg%3E")
        if result:
          st.session_state.google_token = result.get('token')
          st.rerun()
      else:
        st.write("Connected to Google calendar!")
      st.write("Services to Spotify:")
      st.button("Connect", key="spotify_button")
      return openai_chat_model, openai_tts_voice

def homepage_view():
  openai_chat_model, openai_tts_voice = init_homepage()

  openai_client = OpenAIClient(
    st.secrets["OPENAI_API_KEY"],
    chat_model=openai_chat_model,
    tts_voice=openai_tts_voice)

  history_container = st.container(height=500)
  audio_container = st.container()
  util.display_history_messages(history_container)
  audio = util.display_audio_recording(audio_container)

  if audio:
    audio_data = audio.export().read()
    buffer = util.create_memory_file(audio_data, "foo.mp3")
    transcription = openai_client.speech_to_text(buffer)
    util.append_message("user", transcription, audio_data)
    util.display_message(history_container, "user", audio_data, transcription)

    answer = openai_client.chat_completion([
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ])
    answer_audio = openai_client.text_to_speech(answer)
    util.append_message("assistant", answer, answer_audio)
    util.display_message(history_container, "assistant", answer_audio, answer)
    logging.info(f"trying to play {answer}.")