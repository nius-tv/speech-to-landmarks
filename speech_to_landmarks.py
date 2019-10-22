import cv2
import numpy as np
import yaml

from config import *
from mouth_landmarks_generator import MouthLandmarksGenerator


def landmarks_to_image(landmarks, output_file):
	shape = (ORIGINAL_VIDEO_RESOLUTION[1], ORIGINAL_VIDEO_RESOLUTION[0]) # columns, rows
	image = np.zeros(shape, np.uint8)

	color = (255, 255, 255) # white
	for x, y in landmarks['mouth_points']:
		# 3 = radius
		# -1 = thinkness, when value is set to -1, the circle will be filled with color
		cv2.circle(image, (int(x), int(y)), 3, color, -1)

	assert cv2.imwrite(output_file, image)


def load_story():
    with open(STORY_FILE_PATH) as f:
        data = f.read()
    return yaml.load(data, Loader=yaml.FullLoader)


if __name__ == '__main__':
	text = load_story()['text']

	print('Computing mouth landmarks from audio and text')
	mouth_lms = MouthLandmarksGenerator().generate(AUDIO_FILE_PATH, text)

	print('Generating images from mouth landmarks')
	num = len(mouth_lms)
	for i, lm in enumerate(mouth_lms):
		output_file_path = '{}/{:010d}.{}'.format(MOUTH_LMS_IMAGES_DIR_PATH, i + 1, IMG_FMT)
		print(i + 1, '/', num, output_file_path)
		landmarks_to_image(lm, output_file_path)
