import os

AUDIO_FMT = os.environ.get('AUDIO_FMT')
AUDIO_FILE_PATH = '/data/audio.{}'.format(AUDIO_FMT)
END_MOUTH_DURATION = 0.2 # in seconds
FORCED_ALIGNER_URL = 'http://gentle:80/transcriptions?async=false'
FPS = os.environ.get('FPS')
IMG_FMT = os.environ.get('IMG_FMT')
MAX_OFFSET_END = 0.7 # in seconds
MIN_OFFSET_END = 0.3 # in seconds
MIN_TIME_BETWEEN_LMS = 0.3 # in seconds
MOUTH_LMS_FILE_PATH = '/models/mouth-landmarks/{}.json'
MOUTH_LMS_INFERENCE_DIR_PATH = '/data/inference'
MOUTH_LMS_IMAGES_DIR_PATH = '/data/landmarks'
NOT_FOUND_IPA_CODE = 'AA'
NUM_JOBS = 5
REST_IPA_CODE = 'IH'
SCALED_VIDEO_RESOLUTION = (512, 1024) # width, height
SILENT_IPA_CODE = 'P'
STORY_FILE_PATH = '/data/story.yaml'
TEXT_FILE_PATH = '/tmp/transcript.txt'
