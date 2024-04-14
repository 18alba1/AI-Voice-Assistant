from typing import TextIO, Mapping, Sequence

from openai import OpenAI

class OpenAIClient:


  def __init__(
      self, openai_api_key: str, chat_model: str="gpt-3.5-turbo",
      stt_model: str="whisper-1", tts_model: str="tts-1", 
      tts_voice: str="nova"):
    self.client = OpenAI(api_key=openai_api_key)
    self.chat_model = chat_model
    self.stt_model = stt_model
    self.tts_model = tts_model
    self.tts_voice = tts_voice

  def speech_to_text(self, file: TextIO) -> str:
    transcription = self.client.audio.transcriptions.create(
        model=self.stt_model,
        file=file,
    )
    return transcription.text
  
  def text_to_speech(self, text: str) -> bytes:
    response = self.client.audio.speech.create(
        model=self.tts_model,
        voice=self.tts_voice,
        input=text
    )
    return response.read()

  def chat_completion(self, messages: Sequence[Mapping[str, str]]) -> str:
    response = self.client.chat.completions.create(
      model=self.chat_model,
      messages=messages
    )
    return response.choices[0].message.content
