docker run \
	-v $(pwd):/app \
	-v $(pwd)/data:/data \
	--network plasmic \
	-it speech-to-landmarks \
	bash
