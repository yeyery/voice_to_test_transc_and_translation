import webrtcvad
import pyaudio
import time

# Constants for audio capture
FORMAT = pyaudio.paInt16          # 16-bit audio
CHANNELS = 1                      # Mono
RATE = 16000                      # Sample rate in Hz
FRAME_DURATION_MS = 20            # Frame duration (10, 20, or 30 ms)
FRAME_SIZE = int(RATE * FRAME_DURATION_MS / 1000)  # Frame size in samples
BUFFER_SIZE = FRAME_SIZE * 2      # Frame size in bytes (16-bit audio)

# Initialize WebRTC VAD
vad = webrtcvad.Vad()
# Aggressiveness mode (0: least aggressive, 3: most aggressive)
vad.set_mode(3)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open a stream for real-time audio input
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=1,
                    frames_per_buffer=FRAME_SIZE)

print("Listening for speech... (Press Ctrl+C to stop)")

# Continuous loop for speech detection
try:
    while True:
        # Read a frame of audio
        audio_frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

        # Check if the frame contains speech
        is_speech = vad.is_speech(audio_frame, RATE)

        if is_speech:
            print(f"[{time.strftime('%H:%M:%S')}] Speech detected!")

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    # Clean up PyAudio resources
    stream.stop_stream()
    stream.close()
    audio.terminate()
