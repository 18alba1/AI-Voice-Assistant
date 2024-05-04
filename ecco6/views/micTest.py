import speech_recognition as sr

def list_microphone_names():
    microphones = sr.Microphone.list_microphone_names()
    for index, name in enumerate(microphones):
        print(f"Microphone {index}: {name}")

list_microphone_names()
