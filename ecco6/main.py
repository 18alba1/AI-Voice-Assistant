from typing import Tuple

import streamlit as st
import util
from OpenAIClient import OpenAIClient
from streamlit_mic_recorder import mic_recorder
from st_audiorec import st_audiorec
from audiorecorder import audiorecorder


def init_streamlit() -> Tuple[st.selectbox, st.selectbox]:
  st.title("Chatbox")
  if "messages" not in st.session_state:
     st.session_state.messages = []

  with st.sidebar:
    st.title("Ecco6")
    st.info("This app allows you to use chat with ChatGPT using audio.")

    openai_chat_model = st.selectbox(
      "OpenAI chat model",
      ("gpt-4-turbo", "gpt-3.5-turbo")
    )
    openai_tts_voice = st.selectbox(
      "OpenAI voice options",
      ("alloy", "echo", "fable", "onyx", "nova", "shimmer")
    )
    return openai_chat_model, openai_tts_voice

def display_history_messages(container: st.container):
  with container:
    for message in st.session_state.messages:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.audio(message["audio"])

def display_audio_recording(container: st.container) -> audiorecorder:
  with container:
    audio = audiorecorder("Click to record", "Click to stop recording")
    return audio
    
def append_message(role: str, content: str, audio: bytes):
  st.session_state.messages.append({
      "role": role,
      "content": content,
      "audio": audio,
  })

def display_message(container: st.container, role: str, audio: bytes, content: str):
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