import torch
import numpy as np
import pyaudio
import time


# audio vars
CHUNKS = 1024  # number of framees per buffer or chunk of frames
FORMAT = pyaudio.paInt16  # 16 bit resolution
CHANNELS = 1  # Mono (2 for stereo)
FRAME_RATE = 16000  # Hz


def main() -> None:

    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model="silero_vad", force_reload=True)

    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

    # pyaudio stuff
    mic = pyaudio.PyAudio()

    stream = mic.open(
        rate=FRAME_RATE,
        frames_per_buffer=CHUNKS,
        format=FORMAT,
        channels=CHANNELS,
        input=True,
        input_device_index=1
    )

    print("Started Recording")
    while True:
        try:
            # must be 512 for 16000Hz
            audio_data = stream.read(int(CHUNKS/2))

            vad_iter = VADIterator(model)

            # transfrom audio data into usable data similar to wav
            audio_int16 = np.frombuffer(audio_data, np.int16).astype('float32')

            audio_tensor = torch.from_numpy(audio_int16) / 32768.0

            speech_dict = vad_iter(audio_tensor, return_seconds=True)

            if speech_dict:
                print(f"[{time.strftime('%H:%M:%S')}] Speech Detected")
        
        except KeyboardInterrupt:
            print("stopping")
            break








if __name__ == "__main__":
    main()