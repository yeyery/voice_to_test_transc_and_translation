import sounddevice as sd
import queue
import vosk
import json
from transformers import MarianMTModel, MarianTokenizer

# Set parameters
MODEL_PATH = "./vosk-model-small-en-us-0.15/"  # Change if using a different model
SAMPLE_RATE = 16000  # Vosk works best at 16kHz
CHANNELS = 1  # Use mono audio for speech recognition

# Load Vosk model
model = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)

# Load MarianMT for English-to-French translation
marian_model_name = "Helsinki-NLP/opus-mt-en-fr"
tokenizer = MarianTokenizer.from_pretrained(marian_model_name)
translator_model = MarianMTModel.from_pretrained(marian_model_name)

# Queue to store audio data
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    """Callback function to receive audio data from SoundDevice"""
    if status:
        print(f"SoundDevice Error: {status}")
    audio_queue.put(bytes(indata))  # Convert NumPy array to bytes and store in queue

# Function to translate text offline
def translate_to_french(english_text):
    english_text = english_text.strip()  # Remove extra spaces
    if english_text:  # Only process non-empty text
        tokenized_text = tokenizer(english_text, return_tensors="pt", padding=True)
        translated_tokens = translator_model.generate(**tokenized_text)
        french_translation = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        return french_translation
    return "No translation available"


def main():
    """Main function to capture audio and recognize speech in real-time"""
    with sd.RawInputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16", callback=callback):
        print("Listening... Speak into the microphone.")
        
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):  # Process audio in chunks
                result = json.loads(recognizer.Result())
                if result["text"] != "":
                    print("(English):", result["text"])

                    # Translate to French
                    french_translation = translate_to_french(result["text"])
                    print("(French):", french_translation)

try:
    main()
except KeyboardInterrupt:
    print("\nExiting...")