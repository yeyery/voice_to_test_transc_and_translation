import whisper
import sounddevice as sd
import numpy as np
import queue
from transformers import MarianMTModel, MarianTokenizer

# Load the Whisper model for speech-to-text
whisper_model = whisper.load_model("tiny")  # Use "small", "medium", or "large" for better accuracy

# Load MarianMT for English-to-French translation
marian_model_name = "Helsinki-NLP/opus-mt-en-fr"
tokenizer = MarianTokenizer.from_pretrained(marian_model_name)
translator_model = MarianMTModel.from_pretrained(marian_model_name)

# Queue to hold audio chunks
audio_queue = queue.Queue()

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

# Function to transcribe and translate audio continuously
def continuous_transcription_and_translation():
    print("Starting offline transcription and translation... Press Ctrl+C to stop.")

    samplerate = 16000  # Required sampling rate for Whisper
    max_buffer_size = samplerate * 10  # Limit buffer size to 10 seconds

    with sd.InputStream(callback=audio_callback, channels=1, samplerate=samplerate, dtype="float32"):
        audio_buffer = np.zeros((0,), dtype="float32")  # Initialize an empty audio buffer

        try:
            while True:
                # Collect audio from the queue
                while not audio_queue.empty():
                    audio_chunk = audio_queue.get()
                    audio_buffer = np.concatenate((audio_buffer, audio_chunk.flatten()))

                # Trim buffer if it exceeds max size
                if len(audio_buffer) > max_buffer_size:
                    audio_buffer = audio_buffer[-max_buffer_size:]

                # Process audio in ~3-second chunks
                if len(audio_buffer) >= samplerate * 3:
                    audio_data = audio_buffer[:samplerate * 3]
                    audio_buffer = audio_buffer[samplerate * 3:]

                    # Normalize and transcribe audio
                    audio_data = np.clip(audio_data, -1.0, 1.0)
                    result = whisper_model.transcribe(audio_data, language="en", task="transcribe", fp16=False)
                    english_text = result.get("text", "").strip()

                    if english_text:
                        print("(English):", english_text)

                        # Translate to French
                        french_translation = translate_to_french(english_text)
                        print("(French):", french_translation)

        except KeyboardInterrupt:
            print("\nTranscription stopped.")
        except Exception as e:
            print(f"An error occurred: {e}")

# Run the transcription and translation
if __name__ == "__main__":
    continuous_transcription_and_translation()