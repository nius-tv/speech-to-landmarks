import cv2
import glob

from config import *
from scipy import ndimage


if __name__ == '__main__':
    images_dir = '{}/*'.format(MOUTH_LMS_IMAGES_DIR_PATH)
    files = glob.iglob(images_dir)

    for i, image_path in enumerate(files):
        print(i + 1, image_path)
        image = cv2.imread(image_path)
        # Resize image
        image = cv2.resize(image, SCALED_VIDEO_RESOLUTION, interpolation=cv2.INTER_CUBIC)
        # Rotate image
        image = ndimage.rotate(image, ROTATION_ANGLE)
        # Save image
        filename = image_path.split('/')[-1]
        output_file = '{}/{}'.format(MOUTH_LMS_INFERENCE_DIR_PATH, filename)
        cv2.imwrite(output_file, image)
