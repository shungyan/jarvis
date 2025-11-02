import torch
from fastapi import FastAPI, UploadFile, File
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import uvicorn
import tempfile
import os

app = FastAPI()

# ---------------- Load Model Once at Startup ----------------

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    low_cpu_mem_usage=True,
    use_safetensors=True
).to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

# ----------------- HTTP Endpoint -----------------

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Run Whisper
    result = pipe(tmp_path, return_timestamps=True)

    # Clean up temp file
    os.remove(tmp_path)

    return {"text": result["text"], "timestamps": result.get("chunks")}

# ----------------- Run Server -----------------

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=1234, reload=False)
