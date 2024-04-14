import streamlit as st
import util
from OpenAIClient import OpenAIClient
from streamlit_mic_recorder import mic_recorder


def init_streamlit():
  st.title("Ecco6")
  if "messages" not in st.session_state:
     st.session_state.messages = []

def display_history_messages(container: st.container):
  with container:
    for message in st.session_state.messages:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.audio(message["audio"])

def display_audio_recording(container: st.container) -> mic_recorder:
  with container:
    _, col2 = st.columns([0.9, 0.1])
    with col2:
      audio_data = mic_recorder(
          start_prompt="⏺️",
          stop_prompt="⏹️", 
          just_once=True,
          key='recorder')
      return audio_data
    
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
    openai_client = OpenAIClient(st.secrets["OPENAI_API_KEY"])

    init_streamlit()
    history_container = st.container(height=500)
    audio_container = st.container()
    display_history_messages(history_container)
    audio_data = display_audio_recording(audio_container)

    if audio_data:
      buffer = util.create_memory_file(audio_data['bytes'], "foo.mp3")
      transcription = openai_client.speech_to_text(buffer)
      append_message("user", transcription, audio_data['bytes'])
      display_message(history_container, "user", audio_data['bytes'], transcription)

      answer = openai_client.chat_completion([
          {"role": m["role"], "content": m["content"]}
          for m in st.session_state.messages
      ])
      answer_audio = openai_client.text_to_speech(answer)
      append_message("assistant", answer, answer_audio)
      display_message(history_container, "assistant", answer_audio, answer)


if __name__ == "__main__":
    main()