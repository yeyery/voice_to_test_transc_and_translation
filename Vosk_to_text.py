import sounddevice as sd
import queue
import vosk
# used for the language translation
# from transformers import MarianMTModel, MarianTokenizer
import threading
from word2number import w2n

# set the model
MODEL_PATH = "./vosk-model-small-en-us-0.15/"  # Change if using a different model

# audio recording parameters
SAMPLE_RATE = 16000  # Vosk works best at 16kHz
CHANNELS = 1  # Use mono audio for speech recognition
CHUNK_SIZE = 1024 # how many frames in a chunk

# Load Vosk model
model = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)

# Load MarianMT for English-to-French translation
# marian_model_name = "Helsinki-NLP/opus-mt-en-fr"
# tokenizer = MarianTokenizer.from_pretrained(marian_model_name)
# translator_model = MarianMTModel.from_pretrained(marian_model_name)

# Queue to store audio and transcribe data
audio_queue = queue.Queue()
result_queue = queue.Queue()

def callback(indata, frames, time, status):
    """
    This function is required to continuously process audio data
    """
    if status:
        print(f"SoundDevice Error: {status}")

    # input audio data into the queue
    audio_queue.put(bytes(indata))

# Function to translate text offline (UNUSED)
def translate_to_french(english_text):
    """
    This function will translate the transcription from french to english
    """

    english_text = english_text.strip()  # Remove extra spaces
    if english_text:  # Only process non-empty text
        tokenized_text = tokenizer(english_text, return_tensors="pt", padding=True)
        translated_tokens = translator_model.generate(**tokenized_text)
        french_translation = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        return french_translation
    return "No translation available"


def get_number(text: str):
    """
    This function will take in a transcribe sentance and replace the spelled out
    numbers with actual numbers
    """

    # transform to a tuple for faster iteration
    words = tuple(text.split())
    output = []
    i = 0
    
    # use while because indexs may be changing
    while i < len(words):
        j = i
        num = None
        pharse = []
        while j < len(words):
            pharse.append(words[j])
            try:
                # this needs to be here to see if the current word is a number
                w2n.word_to_num(words[j])
                # convert list to str
                num = w2n.word_to_num(" ".join(pharse))

                last_index = j
                j += 1
            except:
                break
        if num:
            output.append(str(num))
            i = last_index + 1
        else:
            output.append(words[i])
            i += 1

    return " ".join(output)
    


def censor_text(text: str):
    """
    This function will take in the produced transcription and censor any
    swears present
    """

    with open("./swears.txt", "r") as file:
        # split by line
        lines = file.read().split("\n")
        # pop the empty string at the end
        lines.pop()
        # split by space
        words = tuple(text.split())
        return " ".join("***" if word.lower() in lines else word for word in words)


def transcribe_audio():
    while True:
        try:
            # get the most recent audio data
            data = audio_queue.get_nowait()
            # this if statement is looking to see if there is silence
            if recognizer.AcceptWaveform(data):  
                result = recognizer.Result().split('"text" : ')[-1][:-2].strip("\"")
                # check to see if there is no silence
                if result != "":
                    result_queue.put(censor_text(get_number(result)))
        except queue.Empty:
            pass


def continuous_transcription():
    """
    Main function to capture audio and recognize speech in real-time
    """

    # This will make sure that all audio recorded will be at 16kHz and each chunk has 1024 frames
    with sd.RawInputStream(samplerate=SAMPLE_RATE,blocksize=CHUNK_SIZE,channels=CHANNELS,dtype="int16",callback=callback,latency="high"):
        threading.Thread(target=transcribe_audio, daemon=True).start()

        while True:
            try:
                # timeout = 2 delays so that I can exit program
                current_text = result_queue.get(timeout=2)

                # continous return of audio data as an iterator
                yield current_text
            except queue.Empty:
                pass
        

if __name__ == "__main__":
    for transcription in continuous_transcription():
        print(transcription)