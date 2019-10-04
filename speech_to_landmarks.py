import cv2
import numpy as np
import redis

from config import *
from mouth_landmarks_generator import MouthLandmarksGenerator


def get_text():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    return r.get(STORY_ID).decode('utf-8') # binary to utf-8 string


def landmarks_to_image(landmarks, output_file):
	shape = (ORIGINAL_VIDEO_RESOLUTION[1], ORIGINAL_VIDEO_RESOLUTION[0]) # columns, rows
	image = np.zeros(shape, np.uint8)

	color = (255, 255, 255) # white
	for x, y in landmarks['mouth_points']:
		# 3 = radius
		# -1 = thinkness, when value is set to -1, the circle will be filled with color
		cv2.circle(image, (int(x), int(y)), 3, color, -1)

	cv2.imwrite(output_file, image)


if __name__ == '__main__':
	print('Computing mouth landmarks from audio and text')
	input_text = get_text()
	mouth_lms = MouthLandmarksGenerator().generate(AUDIO_FILE_PATH, input_text)

	print('Generating images from mouth landmarks')
	num = len(mouth_lms)
	for i, lm in enumerate(mouth_lms):
		output_file_path = '{}/{:010d}.{}'.format(MOUTH_LMS_IMAGES_DIR_PATH, i + 1, IMG_FMT)
		print(i + 1, '/', num, output_file_path)
		landmarks_to_image(lm, output_file_path)
