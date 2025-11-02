FROM python:3.12-slim-trixie

# Install system deps (FFmpeg + curl for uv installer)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# -------- Install uv --------
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# -------- Create app directory --------
WORKDIR /app

# Copy Python app
COPY server.py .
 

# Create requirements
# (Listing explicitly avoids downloading large optional extras)
# RUN echo "torch\ntransformers\ndatasets\ntorchaudio\naccelerate\nfastapi\nuvicorn[standard]" > requirements.txt
RUN uv venv

# Sync environment using uv (installs packages fast + reproducible)
RUN uv pip install transformers datasets[audio] accelerate fastapi uvicorn python-multipart

# Expose server port
EXPOSE 1234

# Run server
CMD ["uv", "run","server.py", "--host", "0.0.0.0", "--port", "1234"]
