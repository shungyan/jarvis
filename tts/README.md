## OpenedAI Speech

A simple self-hosted text-to-speech (TTS) API compatible with OpenAI’s /v1/audio/speech endpoint.

### 🚀 Quick Start
1️⃣ Clone the repository
```bash
git clone https://github.com/matatonic/openedai-speech
cd openedai-speech
```

### 2️⃣ Copy and configure the environment file
```bash
cp sample.env speech.env
```

Edit `speech.env` as needed to configure your model, voice, or server options.

### 3️⃣ Start the service with Docker
```bash
docker compose up -d
```

This will build and run the API at [http://localhost:8000](http://localhost:8000).

### 4️⃣ Generate speech from text
Run this command to test the TTS API and save the result as `speech.mp3`:

#### Linux / macOS:
```bash
curl -s http://localhost:8000/v1/audio/speech -H "Content-Type: application/json" -d '{"input": "The quick brown fox jumped over the lazy dog.", "voice": "alloy"}' > speech.mp3
```

#### Windows (PowerShell / CMD):
```bash
curl -s http://localhost:8000/v1/audio/speech -H "Content-Type: application/json" -d "{\"input\": \"The quick brown fox jumped over the lazy dog.\", \"voice\": \"alloy\"}" > speech.mp3
```