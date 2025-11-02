import speech_recognition as sr
import wave
import datetime
import requests
import json
import time
import pathlib
import sys
import pygame
import tempfile
import uuid

# --- Configuration ---
# Session management uses port 8000 (as specified in your GET/POST requests)
SESSION_URL = "http://127.0.0.1:5678/apps/agents/users/u_123/sessions/s_123"
# Agent execution uses port 5678 (as specified in your /run request)
RUN_URL = "http://127.0.0.1:5678/run"

# Common headers for JSON payloads
HEADERS = {"Content-Type": "application/json"}

SESSION_NOT_FOUND = {"detail": "Session not found"}


HOTWORD = "hey jarvis"
url = "http://localhost:1234/transcribe"

def generate_and_play_tts(
    input_text: str, 
    api_url: str = 'http://localhost:8000/v1/audio/speech', 
    response_format: str = 'mp3' 
):

    # Generate a unique filename using UUID
    unique_name = f"tts_output_{uuid.uuid4()}.{response_format}"
    
    # <--- MODIFIED: Use the system's temporary directory for the file path
    # This keeps temporary files out of the working directory.
    file_path = pathlib.Path(tempfile.gettempdir()) / unique_name 
    
    # 1. Prepare the request payload and headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # The payload structure is based on your curl command's -d data
    payload = {
        "input": input_text,
        "voice": "alloy",
    }
    
    print(f"Sending request to: {api_url}")

    try:
        # 2. Send the POST request
        response = requests.post(api_url, headers=headers, json=payload, stream=True)
        
        # 3. Check for successful response status
        if response.status_code == 200:
            
            # 4. Save the binary content to the specified file
            with open(file_path, 'wb') as f:
                # Use response.iter_content for efficient handling of large binary streams
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print("-" * 40)
            print(f"Success! Audio saved to: {file_path.resolve()}")
            
            # 5. Play the saved audio file
            print("Attempting to play audio...")

            try:
                pygame.mixer.init()
                pygame.mixer.music.load(str(file_path))
                pygame.mixer.music.play()

                # Wait until playback is done
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                file_path.unlink(missing_ok=True)

            except Exception as e:
                print(".")
                # # Handle playback errors, but do NOT stop the cleanup from running!
                # print(f"Warning: Playback error occurred: {e}", file=sys.stderr)

        else:
            # Handle API errors
            print("-" * 40)
            print(f"API Request Failed with Status Code: {response.status_code}", file=sys.stderr)
            print("Response content:", response.text.strip())

    except Exception as e:
        print("-" * 40)
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

def extract_agent_text(response_data):
    """
    Parses the complex agent response array to find the final text response.
    It iterates backward, looking for the last message with a 'model' role
    that contains a 'text' part.
    """
    for message in reversed(response_data):
        try:
            # Check if this message is from the model
            content = message.get('content', {})
            if content.get('role') == 'model':
                # Check if the first part of the content has a 'text' key
                parts = content.get('parts', [])
                if parts and 'text' in parts[0]:
                    return parts[0]['text']
        except Exception:
            # Skip messages that don't match the expected structure
            continue
    
    return "Error: Final text message not found in agent response."

def check_and_create_session():
    """
    Attempts to GET the session. If the response is the specific 'Session not found' 
    JSON, it POSTs to create the session.
    """
    print("--- 1. Checking for existing session (GET) ---")
    try:
        # Request 1: Check session. Chaining .json() here means HTTP errors (like 404 or 500) 
        # that don't return valid JSON will be caught by the outer except block.
        response_data = requests.get(SESSION_URL, headers=HEADERS).json()

        # Check for missing session based on the explicit JSON detail key/value
        if response_data.get("detail") == SESSION_NOT_FOUND.get("detail"):
            print(f"Session not found. Proceeding to create session...")
            
            # Request 2 (Conditional): Create session
            print("\n--- 2. Creating new session (POST) ---")
            try:
                post_response = requests.post(
                    SESSION_URL, 
                    headers=HEADERS
                )
                post_response.raise_for_status() # Check for errors during POST
                print(f"Session created successfully (Status: {post_response.status_code}).")
            except requests.exceptions.RequestException as post_e:
                print(f"Error creating session: {post_e}")
                print(f"Response text: {post_e.response.text if post_e.response else 'N/A'}")
                return False
        
        else:
            # If we successfully got JSON, and it's not the 'not found' message, assume session exists.
            print(f"Session already exists.")
            
    except requests.exceptions.ConnectionError:
        # This occurs if the server (port 8000) is not running
        print(f"Connection Error: Could not connect to the session server at {SESSION_URL}. Is the ADK server running on port 8000?")
        return False
    except requests.exceptions.RequestException as e:
        # Generic request or HTTP error. This now also catches JSONDecodeError if the server returns non-JSON.
        print(f"An error occurred during session check (Server returned non-JSON, non-200, or other issue): {e}")
        return False
        
    return True

def run_agent_query(RUN_QUERY_PAYLOAD):
    """
    Sends the user query to the agent's /run endpoint on port 5678.
    """
    print("\n--- 3. Running Agent Query (POST) ---")
    try:
        # Request 3: Run Query
        response = requests.post(
            RUN_URL, 
            headers=HEADERS, 
            data=json.dumps(RUN_QUERY_PAYLOAD)
        )
        response.raise_for_status()

        print(f"Query sent successfully (Status: {response.status_code}).")
        response_data = response.json()
        
        # --- Updated Logic: Use the robust extractor ---
        agent_text = extract_agent_text(response_data)
        
        print("\nAgent Text Content:")
        print(agent_text)
        return agent_text

    except requests.exceptions.ConnectionError:
        print(f"Connection Error: Could not connect to the run endpoint at {RUN_URL}. Is the ADK server running on port 5678?")
    except requests.exceptions.RequestException as e:
        print(f"Error running agent query: {e}")
        if e.response:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")

def wait_for_enter():
    """Waits for the user to press Enter to start recording."""
    input("\n\n[ READY ] Press ENTER to START recording or CTRL+C to quit.")


def wait_for_hotword(recognizer, mic):
    print("🎧 Listening for hotword 'hey jarvis'...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        try:
            with mic as source:
                audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")

            if HOTWORD in text:
                print("Hotword detected!")
                return
        except sr.UnknownValueError:
            pass
        except KeyboardInterrupt:
            exit(0)


def record_until_silence(recognizer, mic):
    print("Start speaking... (I will stop when silent for 3 seconds)")
    recognizer.pause_threshold = 3.0  # Silence length to stop

    with mic as source:
        audio = recognizer.listen(source)

    # Convert SR audio data → raw WAV bytes
    wav_data = audio.get_wav_data()        # raw WAV-encoded bytes
    sample_width = audio.sample_width      # correct sample width
    sample_rate = audio.sample_rate        # correct sample rate

    #filename = datetime.datetime.now().strftime("jarvis_record_%Y%m%d_%H%M%S.wav")
    filename="jarvis_record.wav"

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(wav_data)

    #print(f"Recording saved as: {filename}")
    return filename


def main():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        try:
            wait_for_enter()
            filename=record_until_silence(recognizer, mic)
            with open(filename, "rb") as f:
                files = {"file": ("audio.wav", f, "audio/wav")}
                response = requests.post(url, files=files).json()

            only_text = response["text"]
            print(only_text)
            get_response = requests.get(SESSION_URL, headers=HEADERS).json()
            
            RUN_QUERY_PAYLOAD = {
                "app_name": "agents",
                "user_id": "u_123",
                "session_id": "s_123",
                "new_message": {
                    "role": "user",
                    "parts": [{"text": only_text}]
                }
            }

            if check_and_create_session():
            # Small delay might be helpful if session creation is highly asynchronous
                time.sleep(0.5) 
                text=run_agent_query(RUN_QUERY_PAYLOAD)
                generate_and_play_tts(text)

        except KeyboardInterrupt:
            print("\nExiting script...")
            break
        except Exception as e:
            print(f"An unexpected error occurred in the main loop: {e}")
            time.sleep(1)

        



if __name__ == "__main__":
    main()
