import os

AUDIO_FMT = os.environ.get('AUDIO_FMT')
AUDIO_FILE_PATH = '/data/audio.{}'.format(AUDIO_FMT)
DEFAULT_MOUTH_IPA_CODE = 'AA'
END_MOUTH_DURATION = 0.4
FORCED_ALIGNER_URL = 'http://gentle:80/transcriptions?async=false'
FPS = float(os.environ.get('FPS'))
IMG_FMT = os.environ.get('IMG_FMT')
MAX_OFFSET_END = 0.3
MIN_OFFSET_END = 0.2
MIN_PERCENTAGE = 0.3
MOUTH_LMS_FILE_PATH = '/models/mouth-landmarks.json'
MOUTH_LMS_INFERENCE_DIR_PATH = '/data/inference'
MOUTH_LMS_IMAGES_DIR_PATH = '/data/landmarks'
NUM_JOBS = 5
ORIGINAL_VIDEO_RESOLUTION = (1080, 1920) # width, height
PERCENTAGE_CLIP = 1
SCALED_VIDEO_RESOLUTION = (512, 1024) # width, height
SILENT_IPA_CODE = 'P'
STORY_FILE_PATH = '/data/story.yaml'
TEXT_FILE_PATH = '/tmp/transcript.txt'
