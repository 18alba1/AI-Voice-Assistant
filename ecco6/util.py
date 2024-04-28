import base64
import io
import logging
from typing import BinaryIO

import streamlit as st

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def display_history_messages(container: st.container):
  """Display all history chatting messages in the Chatbox.
  
  Args:
    container: The container to display the history messages.
  """
  with container:
    for message in st.session_state.messages:
      with st.chat_message(message["role"]):
        st.audio(message["audio"])
        st.markdown(message["content"])
        logging.info(f"display {message['content']} from history")

def display_audio_recording(container: st.container) -> "audiorecorder":
  """Display audio recoriding in the Chatbox.
  
  Args:
    container: The container to display the audio recording
  Returns:
    The recorded audiorecorder.
  """
  from audiorecorder import audiorecorder
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
      if role == "assistant":
          audio_base64 = base64.b64encode(audio).decode()
          html_string = f"""
              <audio controls autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
              </audio>
          """
          sound = st.empty()
          sound.markdown(html_string, unsafe_allow_html=True)
      else:
          st.audio(audio)
      st.markdown(content)

def create_memory_file(content: bytes, filename: str) -> BinaryIO:
  """Create memory file by giving file content and file name.

    Args:
      content: the content in the file.
      filename: the string of the filename.
    Returns:
      BinaryIO of a memory file.
  """
  memory_file = io.BytesIO(content)
  memory_file.name = filename
  return memory_file

def render_image(filepath: str):
  """
  filepath: path to the image. Must have a valid file extension.
  """
  mime_type = filepath.split('.')[-1:][0].lower()
  with open(filepath, "rb") as f:
    content_bytes = f.read()
    content_b64encoded = base64.b64encode(content_bytes).decode()
    image_string = f'data:image/{mime_type};base64,{content_b64encoded}'
  st.image(image_string)