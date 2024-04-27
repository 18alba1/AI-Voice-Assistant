import logging
from typing import Tuple

import streamlit as st
from PIL import Image
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from streamlit_js_eval import get_geolocation

from ecco6 import util
from ecco6.agent import Ecco6Agent
from ecco6.auth import firebase_auth
from ecco6.client.OpenAIClient import OpenAIClient


def init_homepage() -> Tuple[st.selectbox, st.selectbox]:
  """Initialize the Chatbox and the Sidebar of streamlit.
  
  Initialize the session state and the sidebar.

  Returns:
    A tuple cotaining the two selectbox of chat model and tts voice.
  """
  st.title("Chatbox")

  location = get_geolocation()
  if location:
    st.session_state.latitude = location["coords"]["latitude"]
    st.session_state.longitude = location["coords"]["longitude"]

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
    st.button(label='Sign Out', on_click=firebase_auth.sign_out, type='primary')

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
      google_client_config = {
         "web": {
            "client_id": st.secrets["GOOGLE_AUTH"]["CLIENT_ID"],
            "project_id": st.secrets["GOOGLE_AUTH"]["PROJECT_ID"],
            "auth_uri": st.secrets["GOOGLE_AUTH"]["AUTH_URI"],
            "token_uri": st.secrets["GOOGLE_AUTH"]["TOKEN_URI"],
            "auth_provider_x509_cert_url": st.secrets["GOOGLE_AUTH"]["AUTH_PROVIDER_X509_CERT_URL"],
            "client_secret": st.secrets["GOOGLE_AUTH"]["CLIENT_SECRET"],
            "redirect_uris": st.secrets["GOOGLE_AUTH"]["REDIRECT_URIS"],
         }
      }
      scopes = [
         "https://www.googleapis.com/auth/calendar",
         "https://mail.google.com/"
      ]
      flow = InstalledAppFlow.from_client_config(
          google_client_config,
          scopes=scopes,
          redirect_uri = st.secrets["GOOGLE_AUTH"]["REDIRECT_URIS"][0],
      )
      if "google_credentials" not in st.session_state:
        if st.button("Sign in with Google"):
          creds = flow.run_local_server(
            port=9000)
          st.session_state.google_credentials = creds
      else:
        creds = st.session_state.google_credentials
        if not creds.valid or (creds.expired and creds.refresh_token): 
          creds.refresh(Request())
          st.session_state.google_credentials = creds
        st.write("Logged into Google!")

      st.write("Services to Spotify:")
      st.button("Connect", key="spotify_button")
      return openai_chat_model, openai_tts_voice

def homepage_view():
  openai_chat_model, openai_tts_voice = init_homepage()

  openai_client = OpenAIClient(
    st.secrets["OPENAI_API_KEY"],
    chat_model=openai_chat_model,
    tts_voice=openai_tts_voice)
  
  ecco6_agent = Ecco6Agent(
     st.secrets["OPENAI_API_KEY"], 
     google_credentials=st.session_state.google_credentials if "google_credentials" in st.session_state else None,
     chat_model=openai_chat_model)

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

    answer = ecco6_agent.chat_completion([
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ])
    answer_audio = openai_client.text_to_speech(answer)
    util.append_message("assistant", answer, answer_audio)
    util.display_message(history_container, "assistant", answer_audio, answer)
    logging.info(f"trying to play {answer}.")