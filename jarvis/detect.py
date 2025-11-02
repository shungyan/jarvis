import speech_recognition as sr

HOTWORD = "hey jarvis"

def listen_for_hotword():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎧 Listening for 'hey jarvis'... (Ctrl+C to stop)")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        try:
            with mic as source:
                audio = recognizer.listen(source)

            # Convert speech to text
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")

            # Check for hotword
            if HOTWORD in text:
                print("✅ Hotword detected!")
                return "hello"

        except sr.UnknownValueError:
            # No speech detected / could not understand — keep listening
            continue
        except sr.RequestError:
            print("⚠️ Speech Recognition service unavailable.")
            break
        except KeyboardInterrupt:
            print("\n🛑 Exiting...")
            break

if __name__ == "__main__":
    response = listen_for_hotword()
    print(response)
