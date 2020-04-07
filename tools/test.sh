docker build \
-t plasmic-speech-to-landmarks \
.

docker run \
-v $(pwd):/app \
-w /app \
-it plasmic-speech-to-landmarks \
python3 tools/reload.py
