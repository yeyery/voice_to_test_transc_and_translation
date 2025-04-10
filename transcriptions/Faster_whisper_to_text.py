from faster_whisper import WhisperModel
import queue
import numpy as np
import sounddevice as sd
import threading
from transformers import MarianMTModel, MarianTokenizer

MODEL_SIZE = "tiny"

MODEL = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

SAMPLE_RATE = 16000 #Hz

# Load MarianMT for English-to-French translation
# marian_model_name = "Helsinki-NLP/opus-mt-en-fr"
# tokenizer = MarianTokenizer.from_pretrained(marian_model_name)
# translator_model = MarianMTModel.from_pretrained(marian_model_name)

# Queue to store audio data and results
audio_queue = queue.Queue()
result_queue = queue.Queue()

# Function to capture audio in real-time
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

# Function to translate text offline
def translate_to_french(english_text):
    english_text = english_text.strip()  # Remove extra spaces
    if english_text:  # Only process non-empty text
        tokenized_text = tokenizer(english_text, return_tensors="pt", padding=True)
        translated_tokens = translator_model.generate(**tokenized_text)
        french_translation = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        return french_translation
    return "No translation available"

def transcribe_audio():
    max_buffer_size = SAMPLE_RATE * 10  # Limit buffer size to 10 seconds
    audio_buffer = np.zeros((0,), dtype="float32")  # Initialize an empty audio buffer
    
    while True:
        # Collect audio from the queue
        try:
            audio_chunk = audio_queue.get()
            audio_buffer = np.concatenate((audio_buffer, audio_chunk.flatten()))

            # Trim buffer if it exceeds max size
            if len(audio_buffer) > max_buffer_size:
                audio_buffer = audio_buffer[-max_buffer_size:]

            # Process audio in ~3-second chunks
            if len(audio_buffer) >= SAMPLE_RATE * 3:
                audio_data = audio_buffer[:SAMPLE_RATE * 3]
                audio_buffer = audio_buffer[SAMPLE_RATE * 3:]

                # Normalize and transcribe audio
                audio_data = np.clip(audio_data, -1.0, 1.0)
                segments, _ = MODEL.transcribe(audio_data, language="en")
                english_text = " ".join(seg.text for seg in segments)

                if english_text:
                    result_queue.put(english_text)
        
        except queue.Empty:
            continue

# Function to transcribe and translate audio continuously
def continuous_transcription():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, dtype="float32"):
        # start a thread to transcribe audio
        threading.Thread(target=transcribe_audio, daemon=True).start()

        while True:
            try:
                text = result_queue.get(timeout=2)
                yield text
            except queue.Empty:
                pass

        

# Run the transcription and translation
if __name__ == "__main__":
    for transcriptions in continuous_transcription():
        print(f"English: {transcriptions}")