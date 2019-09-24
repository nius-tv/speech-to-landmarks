import cv2
import numpy as np

from config import IMG_FMT, ORIGINAL_VIDEO_RESOLUTION
from mouth_landmarks_generator import MouthLandmarksGenerator


def landmarks_to_image(landmarks, output_file):
	shape = (ORIGINAL_VIDEO_RESOLUTION[1], ORIGINAL_VIDEO_RESOLUTION[0]) # columns, rows
	image = np.zeros(shape, np.uint8)

	color = (255, 255, 255) # white
	for x, y in lm['mouth_points']:
		# 3 = radius
		# -1 = thinkness, when value is set to -1, the circle will be filled with color
		cv2.circle(image, (int(x), int(y)), 3, color, -1)

	cv2.imwrite(output_file, image)


if __name__ == '__main__':
	audio_file_path = '/data/audio.wav'
	text = 'wave glow is awesome'

	print('Computing mouth landmarks from audio and text')
	mouth_lms = MouthLandmarksGenerator().generate(audio_file_path, text)

	print('Generating images from mouth landmarks')
	num = len(mouth_lms)
	for i, lm in enumerate(mouth_lms):
		output_file_path = '/data/mouth-landmarks/{:010d}.{}'.format(i + 1, IMG_FMT)
		print(i + 1, '/', num, output_file_path)
		landmarks_to_image(lm, output_file_path)
