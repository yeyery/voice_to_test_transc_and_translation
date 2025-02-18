import sounddevice as sd
import queue
import vosk
from transformers import MarianMTModel, MarianTokenizer
import threading

# Set parameters
MODEL_PATH = "./vosk-model-small-en-us-0.15/"  # Change if using a different model
SAMPLE_RATE = 16000  # Vosk works best at 16kHz
CHANNELS = 1  # Use mono audio for speech recognition
BLOCK_SIZE = 1024

# Load Vosk model
model = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)

# Load MarianMT for English-to-French translation
# marian_model_name = "Helsinki-NLP/opus-mt-en-fr"
# tokenizer = MarianTokenizer.from_pretrained(marian_model_name)
# translator_model = MarianMTModel.from_pretrained(marian_model_name)

# Queue to store audio data
audio_queue = queue.Queue()
result_queue = queue.Queue()

audio_buffer = bytearray()

def callback(indata, frames, time, status):
    """Callback function to receive audio data from SoundDevice"""
    if status:
        print(f"SoundDevice Error: {status}")

    audio_buffer.extend(indata)
    if len(audio_buffer) >= BLOCK_SIZE:
        audio_queue.put(bytes(indata))
        audio_buffer.clear()

# Function to translate text offline
def translate_to_french(english_text):
    english_text = english_text.strip()  # Remove extra spaces
    if english_text:  # Only process non-empty text
        tokenized_text = tokenizer(english_text, return_tensors="pt", padding=True)
        translated_tokens = translator_model.generate(**tokenized_text)
        french_translation = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        return french_translation
    return "No translation available"

def censor_text(text: str):
    with open("./swears.txt", "r") as file:
        lines = file.read().split("\n")
        lines.pop()
        words = text.split()
        return " ".join("***" if word.lower() in lines else word for word in words)

def transcribe_audio():
    while True:
        try:
            data = audio_queue.get_nowait()
            if len(data) >= BLOCK_SIZE:
                if recognizer.AcceptWaveform(data):  # Process audio in chunks
                    result = recognizer.Result().split('"text" : ')[-1][:-2].strip("\"")
                    if result != "":
                        result_queue.put(censor_text(result))
        except queue.Empty:
            continue


def continuous_transcription():
    """Main function to capture audio and recognize speech in real-time"""
    with sd.RawInputStream(samplerate=SAMPLE_RATE,blocksize=BLOCK_SIZE,channels=CHANNELS,dtype="int16",callback=callback):
        threading.Thread(target=transcribe_audio, daemon=True).start()

        while True:
            try:
                current_text = result_queue.get(timeout=2)
                yield current_text
            except queue.Empty:
                pass
        

if __name__ == "__main__":
    for transcription in continuous_transcription():
        print(transcription)