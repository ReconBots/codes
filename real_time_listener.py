import pyaudio
import wave
import numpy as np
import time

from google.cloud import speech
import io
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 500  # Adjust this value based on the background noise level
SILENCE_DURATION = 2  # Seconds of silence to stop recording
FILENAME_PREFIX = "audio_snippet"

def is_silent(data_chunk):
    """Check if the chunk of audio is silent."""
    audio_data = np.frombuffer(data_chunk, dtype=np.int16)
    return np.abs(audio_data).mean() < SILENCE_THRESHOLD

def save_audio(filename, frames):
    """Save audio frames to a .wav file."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def record_audio():
    """Continuously listens to the microphone and saves audio excerpts."""
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    print("Listening... Press Ctrl+C to stop.")

    audio_frames = []
    silent_chunks = 0
    file_counter = 0
    frame_counter = 0

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            # print(data)
            if is_silent(data):
                silent_chunks += 1
            else:
                print("ouvindo...")
                silent_chunks = 0                
                frame_counter += 1
            
            if frame_counter>0:
                audio_frames.append(data)
 
            # Save the audio file if silence is detected for a specific duration
            if silent_chunks > (RATE // CHUNK * SILENCE_DURATION):
                print("estou aqui")
                if frame_counter>4:
                    filename = f"./data/{FILENAME_PREFIX}_{file_counter}.wav"
                    save_audio(filename, audio_frames)
                    print(f"Saved: {filename}")
                    print('\ndecifrando...')
                    transcrever_audio(filename)

                    file_counter += 1
                    
                audio_frames = []
                silent_chunks = 0  # Reset silence counter
                frame_counter = 0
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

def transcrever_audio(audio_path):
    client = speech.SpeechClient()

    with io.open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # Usando LINEAR16 para .wav
        sample_rate_hertz=16000,  # Taxa de amostragem do áudio
        language_code="en-US",  # Idioma do áudio
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        audio = result.alternatives[0].transcript.lower()
        chamada(audio)
        print("Transcrição:", result.alternatives[0].transcript)

def chamada(audio):
    comando = [ # os 'sarah', não precisa, pois já tem um 'sara' em 'sarah'
        "ok sara",
        "okay sara",
        "hi sara",
        "alô sara",
        "hello sara",
        ]
    for item in comando:
        if item in audio:
            leituraCoamndo = comandos(audio.split(item)[1])
            if leituraCoamndo:
                break

def comandos(comand):
    finish = True
    if 'follow me' in comand:
        print('ação: seguir pessoa')
    elif 'get it' in comand:
        print('ação: ativando garra')
    elif 'talk' in comand:
        print('ação: falando')
    elif 'find the leader' in comand:
        print('ação: mirando na pessoa')
    else:
        print(f"no '{comand}', não encontrei o comando registrado, tente novamente mais tarde")
        finish = False
    
    return finish

if __name__ == "__main__":
    record_audio()