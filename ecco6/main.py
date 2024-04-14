import io
from OpenAIClient import OpenAIClient

import streamlit as st
from streamlit_mic_recorder import mic_recorder

st.title("Ecco6")

openai_client = OpenAIClient(st.secrets["OPENAI_API_KEY"])

history_container = st.container(height=500)
audio_container = st.container()

if "messages" not in st.session_state:
    st.session_state.messages = []

with history_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            st.audio(message["audio"])


# Adding the record button at the end
with audio_container:
    col1, col2 = st.columns([0.9, 0.1])
    with col2:
        audio_data = mic_recorder(
            start_prompt="⏺️",
            stop_prompt="⏹️", 
            just_once=True,
            key='recorder')

# Use the audio_data as needed
if audio_data:
    buffer = io.BytesIO(audio_data['bytes'])
    buffer.name = "file.mp3"
    transcription = openai_client.speech_to_text(buffer)
    st.session_state.messages.append({
        "role": "user",
        "content": transcription,
        "audio": audio_data['bytes'],
    })
    with history_container:
        with st.chat_message("user"):
            st.audio(audio_data['bytes'])
            st.markdown(transcription)

    answer = openai_client.chat_completion([
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ])
    answer_audio = openai_client.text_to_speech(answer)
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "audio": answer_audio,
    })
    with history_container:
        with st.chat_message("assistant"):
            st.audio(answer_audio)
            st.markdown(answer)
