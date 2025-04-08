import wave
import pyaudio

# yeti microphone is 2

FRAMES_PER_BUFFER = 1024  # number of framees per buffer or chunk of frames
FORMAT = pyaudio.paInt16  # 16 bit resolution
CHANNELS = 1  # Mono (2 for stereo)
RATE = 16000  # Hz


def get_connected_devicees():
    p = pyaudio.PyAudio()

    for i in range(p.get_device_count()):
        print(i)
        dev = p.get_device_info_by_index(i)
        print(dev.get("name"))
        print("\n")

    p.terminate()


def record_audio():
    p = pyaudio.PyAudio()

    stream = p.open(
        rate=RATE,
        frames_per_buffer=FRAMES_PER_BUFFER,
        format=FORMAT,
        channels=CHANNELS,
        input=True,
        input_device_index=2
    )

    print("Recording")

    seconds = 5
    chunks = []

    # unit check (frames/second / frames/buffer * seconds = buffer) so how many buffers / chunks of framees
    for i in range(0, int(RATE/FRAMES_PER_BUFFER * seconds)):
        # reads so many frames
        data = stream.read(FRAMES_PER_BUFFER)
        # list of chunks of frames
        chunks.append(data)

    print("print stop recording")

    stream.stop_stream()
    stream.close()

    p.terminate()

    with wave.open("test.wav", "wb") as file:
        file.setnchannels(CHANNELS)
        file.setsampwidth(p.get_sample_size(FORMAT))
        file.setframerate(RATE)
        file.writeframes(b"".join(chunks))


if __name__ == "__main__":
    record_audio()
