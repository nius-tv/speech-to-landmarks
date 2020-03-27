import cv2
import numpy as np
import yaml

from config import *
from google.cloud import error_reporting
from joblib import Parallel, delayed
from mouth_landmarks_generator import MouthLandmarksGenerator


def landmarks_to_image(num, i, landmarks):
	output_file_path = '{}/{:010d}.{}'.format(MOUTH_LMS_IMAGES_DIR_PATH, i + 1, IMG_FMT)
	print(i + 1, '/', num, output_file_path)

	shape = (SCALED_VIDEO_RESOLUTION[1], SCALED_VIDEO_RESOLUTION[0]) # columns, rows
	image = np.zeros(shape, np.uint8)

	color = (255, 255, 255) # white
	for x, y in landmarks['mouth_points']:
		# 3 = radius
		# -1 = thinkness, when value is set to -1, the circle will be filled with color
		cv2.circle(image, (int(x), int(y)), 3, color, -1)

	assert cv2.imwrite(output_file_path, image)


def load_story():
	with open(STORY_FILE_PATH) as f:
		data = f.read()
	return yaml.load(data, Loader=yaml.FullLoader)


def save_story(data):
	with open(STORY_FILE_PATH, 'w') as f:
		yaml.dump(data, f, default_flow_style=False)


if __name__ == '__main__':
	error_client = error_reporting.Client()
	try:
		story = load_story()
		text = story['text']

		print('Computing mouth landmarks from audio and text')
		forced_aligner_data, mouth_lms, oov_frames = MouthLandmarksGenerator(story).generate(AUDIO_FILE_PATH, text)

		print('Saving out-of-vocabulary frames')
		story['forcedAligner'] = forced_aligner_data
		story['outOfVocabularyFrames'] = oov_frames
		save_story(story)

		print('Generating images from mouth landmarks')
		num = len(mouth_lms)

		Parallel(n_jobs=NUM_JOBS)(
			delayed(landmarks_to_image)(num, i, lm)
			for i, lm in enumerate(mouth_lms)
		)
	except Exception:
		error_client.report_exception()
		raise
