import subprocess

from config import *
from google.cloud import error_reporting


if __name__ == '__main__':
    error_client = error_reporting.Client()
    try:
        cmd = 'ffmpeg \
            -y \
            -i {input_dir_path}/%010d.{img_fmt} \
            -vf scale={width}:{height},transpose=2 \
            {output_dir_path}/%010d.{img_fmt}'.format(
                input_dir_path=MOUTH_LMS_IMAGES_DIR_PATH,
                img_fmt=IMG_FMT,
                width=SCALED_VIDEO_RESOLUTION[0],
                height=SCALED_VIDEO_RESOLUTION[1],
                output_dir_path=MOUTH_LMS_INFERENCE_DIR_PATH)
        subprocess.call(['bash', '-c', cmd])
    except Exception:
        error_client.report_exception()
        raise
