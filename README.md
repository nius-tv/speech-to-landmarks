docker build \
	-t speech-to-landmarks \
	.

docker network create plasmic

docker run \
	-v $(pwd):/app \
	-v $(pwd)/data:/data \
	-v $(pwd)/data/mouth-landmarks.json:/models/mouth-landmarks.json \
	--network plasmic \
	-it speech-to-landmarks \
	bash

export AUDIO_FMT=wav
export FPS=30
export IMG_FMT=png
python3 speech_to_landmarks.py
python3 prepare_for_inference.py
