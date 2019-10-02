import os

AUDIO_FILE_PATH = '/data/audio.wav'
DEFAULT_MOUTH_IPA_CODE = 'AA'
FORCED_ALIGNER_URL = 'http://gentle:80/transcriptions?async=false'
FPS = 30
IMG_FMT = 'png'
INPUT_TEXT = os.environ.get('INPUT_TEXT')
MIN_PERCENTAGE = 0.7
MOUTH_LMS_FILE_PATH = '/models/mouth-landmarks.json'
MOUTH_LMS_INFERENCE_DIR_PATH = '/data/inference'
MOUTH_LMS_IMAGES_DIR_PATH = '/data/landmarks'
OFFSET_END = 0.1
ORIGINAL_VIDEO_RESOLUTION = (1080, 1920) # width, height
PERCENTAGE_CLIP = 3
ROTATION_ANGLE = 90
SCALED_VIDEO_RESOLUTION = (512, 1024) # width, height
SILENT_IPA_CODE = 'P'
TEXT_FILE_PATH = '/tmp/transcript.txt'
