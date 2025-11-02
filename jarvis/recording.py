import pyaudio
import wave
import datetime

def record_audio():
    # Audio settings
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    # Output filename with timestamp
    filename = datetime.datetime.now().strftime("recording_%Y%m%d_%H%M%S.wav")

    audio = pyaudio.PyAudio()

    # Open microphone stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("🎙️ Recording... Press CTRL+C to stop.")

    frames = []

    try:
        while True:
            data = stream.read(CHUNK)
            frames.append(data)

    except KeyboardInterrupt:
        print("\n🛑 Stopped recording.")

    # Stop and close
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save file
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    print(f"✅ Saved recording to: {filename}")

if __name__ == "__main__":
    record_audio()
