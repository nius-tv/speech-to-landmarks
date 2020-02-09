import json
import math
import random
import requests

from config import *


class MouthLandmarksGenerator(object):

    NOT_FOUND_IN_AUDIO = 'not-found-in-audio'
    OUT_OF_VOCABULARY = 'OOV'

    def __init__(self):
        self.mouth_lms_points = self._get_mouth_lms_points()
        # All mouth landmarks have the same number of points.
        # Here we can use the default ipa code to obtain the number of mouth points.
        self.num_mouth_points = len(self.mouth_lms_points[DEFAULT_MOUTH_IPA_CODE])

    def _adjust_lms(self, mouth_lms):
        old_mouth = None
        new_mouth_lms = []

        for i, mouth_lm in enumerate(mouth_lms):
            mouth_start = mouth_lm['start']
            # Checks if there is a "gap"/"silence" between mouths landmarks.
            if i == 0 and mouth_start > 0:
                init_start = mouth_start - random.uniform(INIT_MIN_OFFSET, INIT_MAX_OFFSET)
                if init_start < 0:
                    init_start = 0

                new_mouth_lms.append({
                    'ipa_code': SILENT_IPA_CODE,
                    'start': 0,
                    'end': init_start
                })
                new_mouth_lms.append({
                    'ipa_code': SILENT_IPA_CODE,
                    'start': init_start,
                    'end': mouth_start
                })
            if i != 0 and mouth_start - old_mouth['end'] > 0:
                old_mouth['end'] = mouth_start

            new_mouth_lms.append(mouth_lm)
            old_mouth = mouth_lm

        # Delay last mouth landmark
        mouth_lm['end'] += END_MOUTH_DURATION

        # Add ending mouth position
        offset = random.uniform(MIN_OFFSET_END, MAX_OFFSET_END)
        new_mouth_lms.append({
            'ipa_code': SILENT_IPA_CODE,
            'start': mouth_lm['end'],
            'end': mouth_lm['end'] + offset
        })
        new_mouth_lms.append({
            'ipa_code': SILENT_IPA_CODE
        })

        return new_mouth_lms

    def _check_mouth_lms(self, mouth_lms):
        num = len(mouth_lms)

        # Fixes issue with Gentle's output
        for i, mouth_lm in enumerate(mouth_lms):
            if i + 1 == num:
                break
            if i > 0 and old_mouth['end'] > mouth_lm['start']:
                old_mouth['end'] = mouth_lm['start']
            old_mouth = mouth_lm

        # Skip landmarks
        new_mouth_lms = []
        tmp_mouth_lms = None
        for i, mouth_lm in enumerate(mouth_lms):
            if tmp_mouth_lms is not None:
                mouth_lm['start'] = tmp_mouth_lms['start']
                tmp_mouth_lms = None

            if i + 1 == len(mouth_lms):
                new_mouth_lms.append(mouth_lm)
                continue

            if mouth_lm['end'] - mouth_lm['start'] < MIN_TIME_BETWEEN_LMS:
                tmp_mouth_lms = mouth_lm
                continue

            new_mouth_lms.append(mouth_lm)

        return new_mouth_lms

    def _compute_mouth_lms(self, forced_aligner_data):
        mouth_lms = []
        mouth_end = 0
        not_found = False

        for word in forced_aligner_data['words']:
            if word['case'] == self.NOT_FOUND_IN_AUDIO and not not_found:
                print('not-found-in-audio:', word['word'])
                mouth_start = mouth_end
                not_found = True
                continue
            elif word['case'] == self.NOT_FOUND_IN_AUDIO and not_found:
                print('not-found-in-audio:', word['word'])
                continue
            elif not_found:
                mouth_lms.append({
                    'ipa_code': self.NOT_FOUND_IN_AUDIO,
                    'start': mouth_start,
                    'end': word['start']
                })
                not_found = False

            mouth_start = word['start']
            mouth_end = mouth_start
            for phone in word['phones']:
                # Extract IPA code
                phone_name = phone['phone']
                ipa_code = phone_name.split('_')[0].upper() # phone name example: "ow_E"
                # Compute start and end
                mouth_end += phone['duration']
                mouth_lms.append({
                    'ipa_code': ipa_code,
                    'start': mouth_start,
                    'end': mouth_end
                })
                mouth_start = mouth_end

        return mouth_lms

    def _execute_forced_aligner(self, audio_file_path, text_file_path):
        files = {
            'audio': open(audio_file_path, 'rb'),
            'transcript': open(text_file_path, 'rb')
        }
        res = requests.post(FORCED_ALIGNER_URL, files=files)
        return res.json()

    def _get_mouth_lms_points(self):
        with open(MOUTH_LMS_FILE_PATH) as f:
            data = f.read()
        return json.loads(data)

    def _interpolate_mouth_lms(self, mouth_lms):
        int_mouth_lms = []
        oov_frames = {}
        num = len(mouth_lms)

        for i, mouth_lm in enumerate(mouth_lms):
            ipa_code = mouth_lm['ipa_code']
            # Select next mouth landmarks
            if i + 1 == num:
                break
            next_ipa_code = mouth_lms[i + 1]['ipa_code']
            # Calculate interpolated mouth points
            start_frame = math.floor(mouth_lm['start'] * FPS)
            end_frame = math.floor(mouth_lm['end'] * FPS)
            int_mouth_lms, oov_frames = self._interpolate_mouth_points(int_mouth_lms, oov_frames,
                                                                       start_frame, end_frame,
                                                                       ipa_code, next_ipa_code)

        return int_mouth_lms, oov_frames

    def _interpolate_mouth_points(self, int_mouth_lms, oov_frames, start_frame, end_frame,
                                  ipa_code, next_ipa_code):
        for i in range(start_frame, end_frame):
            percentage = float(i - start_frame + 1) / float(end_frame - start_frame)

            mouth_points = []
            for a in range(self.num_mouth_points):
                # Check if ipa code exists
                if ipa_code not in self.mouth_lms_points \
                    and not ipa_code in [self.NOT_FOUND_IN_AUDIO, self.OUT_OF_VOCABULARY]:
                    print('ipa_code:', ipa_code)
                    raise
                elif ipa_code in [self.NOT_FOUND_IN_AUDIO, self.OUT_OF_VOCABULARY]:
                    ipa_code = DEFAULT_MOUTH_IPA_CODE
                    oov_frames[start_frame] = end_frame

                x, y = self.mouth_lms_points.get(ipa_code)[a]
                # Check if ipa code exists
                if next_ipa_code not in self.mouth_lms_points \
                    and not next_ipa_code in [self.NOT_FOUND_IN_AUDIO, self.OUT_OF_VOCABULARY]:
                    print('next_ipa_code:', next_ipa_code)
                    raise
                elif next_ipa_code in [self.NOT_FOUND_IN_AUDIO, self.OUT_OF_VOCABULARY]:
                    next_ipa_code = DEFAULT_MOUTH_IPA_CODE
                    oov_frames[start_frame] = end_frame

                target_x, target_y = self.mouth_lms_points.get(next_ipa_code)[a]
                # Calculate interpolated points
                int_x = x + ((target_x - x) * percentage)
                int_y = y + ((target_y - y) * percentage)
                mouth_points.append((int_x, int_y))

            int_mouth_lms.insert(i, {
                'ipa_code': ipa_code,
                'next_ipa_code': next_ipa_code,
                'mouth_points': mouth_points
            })

        return int_mouth_lms, oov_frames

    def _save_text(self, text):
        with open(TEXT_FILE_PATH, 'w') as f:
            f.write(text)

    def generate(self, audio_file_path, text):
        self._save_text(text)
        forced_aligner_data = self._execute_forced_aligner(audio_file_path,
                                                           TEXT_FILE_PATH)
        print('forced aligner data:\n', json.dumps(forced_aligner_data, indent=True))

        mouth_lms = self._compute_mouth_lms(forced_aligner_data)
        mouth_lms = self._adjust_lms(mouth_lms)
        mouth_lms = self._check_mouth_lms(mouth_lms)
        mouth_lms, oov_frames = self._interpolate_mouth_lms(mouth_lms)
        return forced_aligner_data, mouth_lms, oov_frames
