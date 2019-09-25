docker build \
	-t speech-to-landmarks \
	.

docker run \
	-v $(pwd)/speech-to-landmarks:/app \
	-v $(pwd)/data/speech-to-landmarks:/data \
	-v $(pwd)/data/mouth-landmarks.json:/data/mouth-landmarks.json \
	-v $(pwd)/data/audio.wav:/data/audio.wav \
	--network plasmic \
	-it speech-to-landmarks \
	bash

python3 speech_to_landmarks.py
python3 prepare_for_inference.py
