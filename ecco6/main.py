from typing import Tuple

import streamlit as st
import util
from OpenAIClient import OpenAIClient
from streamlit_mic_recorder import mic_recorder
from st_audiorec import st_audiorec
from audiorecorder import audiorecorder
from streamlit_oauth import OAuth2Component


def init_streamlit() -> Tuple[st.selectbox, st.selectbox]:
  """Initialize the Chatbox and the Sidebar of streamlit.
  
  Initialize the session state and the sidebar.

  Returns:
    A tuple cotaining the two selectbox of chat model and tts voice.
  """
  st.title("Chatbox")

  if "messages" not in st.session_state:
     st.session_state.messages = []

  with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>Ecco6</h1>", unsafe_allow_html=True)
    st.info("This app allows you to use ChatGPT by audio commands and connect to more services.")

    openai_chat_model = st.selectbox(
      "OpenAI chat model",
      ("gpt-4-turbo", "gpt-3.5-turbo")
    )
    openai_tts_voice = st.selectbox(
      "OpenAI voice options",
      ("alloy", "echo", "fable", "onyx", "nova", "shimmer")
    )
  
    st.write("Services to Google:")
    authorization_url = st.secrets["AUTHORIZATION_URL"]
    token_url = st.secrets["TOKEN_URL"]
    revoke_url = st.secrets["REDIRECT_URI"][0]
    client_id = st.secrets["CLIENT_ID"]
    client_secret = st.secrets["CLIENT_SECRET"]
    redirect_uri = st.secrets["REDIRECT_URI"][0]
    scopes = "https://www.googleapis.com/auth/calendar"
    oauth2 = OAuth2Component(client_id, client_secret, authorization_url, token_url, token_url, revoke_url)
    if 'google_token' not in st.session_state:
      result = oauth2.authorize_button("Continue with Google", redirect_uri, scopes, icon="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 48 48'%3E%3Cdefs%3E%3Cpath id='a' d='M44.5 20H24v8.5h11.8C34.7 33.9 30.1 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 4.1 29.6 2 24 2 11.8 2 2 11.8 2 24s9.8 22 22 22c11 0 21-8 21-22 0-1.3-.2-2.7-.5-4z'/%3E%3C/defs%3E%3CclipPath id='b'%3E%3Cuse xlink:href='%23a' overflow='visible'/%3E%3C/clipPath%3E%3Cpath clip-path='url(%23b)' fill='%23FBBC05' d='M0 37V11l17 13z'/%3E%3Cpath clip-path='url(%23b)' fill='%23EA4335' d='M0 11l17 13 7-6.1L48 14V0H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%2334A853' d='M0 37l30-23 7.9 1L48 0v48H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%234285F4' d='M48 48L17 24l-4-3 35-10z'/%3E%3C/svg%3E")
      if result:
        st.session_state.google_token = result.get('token')
        st.rerun()
    else:
      st.write("Connected to Google calendar!")
    st.write("Services to Spotify:")
    st.button("Connect", key="spotify_button")
    return openai_chat_model, openai_tts_voice


def display_history_messages(container: st.container):
  """Display all history chatting messages in the Chatbox.
  
  Args:
    container: The container to display the history messages.
  """
  with container:
    for message in st.session_state.messages:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.audio(message["audio"])

def display_audio_recording(container: st.container) -> audiorecorder:
  """Display audio recoriding in the Chatbox.
  
  Args:
    container: The container to display the audio recording
  Returns:
    The recorded audiorecorder.
  """
  with container:
    audio = audiorecorder("Click to record", "Click to stop recording")
    return audio
    
def append_message(role: str, content: str, audio: bytes):
  """Append a message to the session state.
  
  Args:
    role: The role of the message, can be user or assistant.
    content: The content of the message.
    audio: Bytes of the audio recoriding, which is corresponds to the
      content.
  """
  st.session_state.messages.append({
      "role": role,
      "content": content,
      "audio": audio,
  })

def display_message(container: st.container, role: str, audio: bytes, content: str):
  """Display a single message.
  
  Args:
    container: The container to display the message.
    role: The role of the message, can be user or assistant.
    audio: Bytes of the audio recoriding, which is corresponds to the
      content.
    content: The content of the message.
  """
  with container:
    with st.chat_message(role):
      st.audio(audio)
      st.markdown(content)

def main():
    openai_chat_model, openai_tts_voice = init_streamlit()

    openai_client = OpenAIClient(
      st.secrets["OPENAI_API_KEY"],
      chat_model=openai_chat_model,
      tts_voice=openai_tts_voice) 

    history_container = st.container(height=500)
    audio_container = st.container()
    display_history_messages(history_container)
    audio = display_audio_recording(audio_container)

    if audio:
      audio_data = audio.export().read()
      buffer = util.create_memory_file(audio_data, "foo.mp3")
      transcription = openai_client.speech_to_text(buffer)
      append_message("user", transcription, audio_data)
      display_message(history_container, "user", audio_data, transcription)

      answer = openai_client.chat_completion([
          {"role": m["role"], "content": m["content"]}
          for m in st.session_state.messages
      ])
      answer_audio = openai_client.text_to_speech(answer)
      append_message("assistant", answer, answer_audio)
      display_message(history_container, "assistant", answer_audio, answer)


if __name__ == "__main__":
    main()