import pyaudio
from vosk import Model, KaldiRecognizer
import json


def main():

    FRAMES_PER_BUFFER = 1024  # number of frames per buffer or chunk of frames
    FORMAT = pyaudio.paInt16  # 16 bit resolution
    CHANNELS = 1  # Mono (2 for stereo)
    FRAME_RATE = 16000  # Hz

    model = Model("./vosk-model-small-en-us-0.15/")

    recognizer = KaldiRecognizer(model, FRAME_RATE)

    mic = pyaudio.PyAudio()

    stream = mic.open(
        rate=FRAME_RATE,
        frames_per_buffer=FRAMES_PER_BUFFER,
        format=FORMAT,
        channels=CHANNELS,
        input=True,
        input_device_index=1
    )

    stream.start_stream()

    while True:
        try:
            data = stream.read(FRAMES_PER_BUFFER)

            if recognizer.AcceptWaveform(data):
                res = recognizer.Result()
                data = json.loads(res)
                print(data["text"])
        except KeyboardInterrupt:
            print("Stopping the program")
            stream.stop_stream()
            stream.close()
            break

if __name__ == "__main__":
     main()
