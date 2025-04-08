"""
This file is for the whisper test
"""

import whisper
import torch
import pyaudio
import queue
import threading
import signal
import time
import numpy as np
import torch.nn.functional as F

# audio vars
CHUNKS = 1024  # number of framees per buffer or chunk of frames
FORMAT = pyaudio.paInt16  # 16 bit resolution
CHANNELS = 1  # Mono (2 for stereo)
FRAME_RATE = 16000  # Hz

# say which model we are using
model = whisper.load_model("tiny")

# create a queue data structure. last in first out
audio_queue = queue.Queue()

# global flag showing recording state
recording = True

# exit event for threads
exit_event = threading.Event()

vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model="silero_vad", force_reload=True)

(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

def is_speech(audio_data):
    """
    Uses Silero VAD to check if the given audio contains speech.
    """
    audio_tensor = torch.from_numpy(audio_data).float()
    audio_tensor = audio_tensor.unsqueeze(0)  # Add batch dimension
    audio_tensor = F.pad(audio_tensor, (0, FRAME_RATE - audio_tensor.shape[1]))  # Pad to 1s

    speech_timestamps = get_speech_timestamps(audio_tensor, vad_model, sampling_rate=FRAME_RATE)
    return len(speech_timestamps) > 0  # True if speech is detected

def record_audio() -> None:
    """
    This function will capture audio from the mic
    """
    
    # state that th recording variable is a global one
    global recording

    mic = pyaudio.PyAudio()

    stream = mic.open(
        rate=FRAME_RATE,
        frames_per_buffer=CHUNKS,
        format=FORMAT,
        channels=CHANNELS,
        input=True,
        input_device_index=1
    )

    stream.start_stream()

    print("start stream")

    
    while not exit_event.is_set():
        data = stream.read(int(CHUNKS/2), exception_on_overflow=False)
        audio_queue.put(data)
        
    

    stream.stop_stream()
    stream.close()
    mic.terminate()
    exit(0)

def process_audio() -> None:
    """
    This function will process the audio to text
    """

    global recording

    audio_buffer = []

    
    while not exit_event.is_set() or not audio_queue.empty():
        try:
            data = audio_queue.get(timeout=0.5)
            audio_buffer.append(data)

            # process only 1 second of audio
            if len(audio_buffer) >= int(FRAME_RATE/CHUNKS * 2):

                # create array from audio in the buffer. for int16 you need to normalize by deviding by 32767 
                audio_data = np.frombuffer(b"".join(audio_buffer), dtype=np.int16).astype(np.float32) / 32768.0

                # clear the buffer when finished
                audio_buffer = []
                
                if is_speech(audio_data):
                    print("[Speech detected] Processing...")
                    results = model.transcribe(audio_data, fp16=False)
                    print("Transcription:", results["text"])
                else:
                    print("[No speech detected] Skipping.")



        except queue.Empty:
            continue


def signal_handler(signum, frame):
    exit_event.set()


def main():

    signal.signal(signal.SIGINT, signal_handler)
    record_thread = threading.Thread(target=record_audio)
    process_thread = threading.Thread(target=process_audio)

    record_thread.start()
    process_thread.start()

    # this checks every 1/3 of second if the ctrl+C has been pressed    
    while not exit_event.is_set():
        time.sleep(0.3)
    

    record_thread.join()
    process_thread.join()


if __name__ == "__main__":
    main()