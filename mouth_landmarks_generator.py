import config
import json
import math
import random
import requests


class MouthLandmarksGenerator(object):

    NOT_FOUND_IN_AUDIO = 'not-found-in-audio'
    OUT_OF_VOCABULARY = 'OOV'

    def __init__(self, model_name):
        self.FPS = float(config.FPS)
        self.mouth_lms_points = self._get_mouth_lms_points(model_name)
        # All mouth landmarks have the same number of points.
        # Here we can use the default ipa code to obtain the number of mouth points.
        self.num_mouth_points = len(self.mouth_lms_points[config.NOT_FOUND_IPA_CODE])

    def _adjust_lms(self, mouth_lms):
        old_mouth = None
        new_mouth_lms = []

        for i, mouth_lm in enumerate(mouth_lms):
            mouth_start = mouth_lm['start']
            # Checks if there is a "gap"/"silence" between initial mouths landmarks
            if i == 0 and mouth_start > 0:
                new_mouth_lms.append({
                    'ipa_code': config.SILENT_IPA_CODE,
                    'start': 0,
                    'end': mouth_start - config.INIT_MOUTH_DURATION
                })
                new_mouth_lms.append({
                    'ipa_code': config.SILENT_IPA_CODE,
                    'start': mouth_start - config.INIT_MOUTH_DURATION,
                    'end': mouth_start
                })
            # Checks if there is a big "gap"/"silence" between mouths landmarks
            if i != 0 and mouth_start - old_mouth['end'] > config.MAX_DURATION_BETWEEN_LMS:
                offset = (mouth_start - old_mouth['end']) / 2
                new_mouth_lms.append({
                    'ipa_code': config.REST_IPA_CODE,
                    'start': old_mouth['end'],
                    'end': mouth_start - offset
                })
                new_mouth_lms.append({
                    'ipa_code': config.REST_IPA_CODE,
                    'start': mouth_start - offset,
                    'end': mouth_start
                })
            # Checks if there is a small "gap"/"silence" between mouths landmarks
            elif i != 0 and mouth_start - old_mouth['end'] > 0:
                old_mouth['end'] = mouth_start

            new_mouth_lms.append(mouth_lm)
            old_mouth = mouth_lm

        # Delay last mouth landmark
        mouth_lm['end'] += config.END_MOUTH_DURATION

        # Add ending mouth position
        offset = random.uniform(config.MIN_OFFSET_END, config.MAX_OFFSET_END)
        new_mouth_lms.append({
            'ipa_code': config.SILENT_IPA_CODE,
            'start': mouth_lm['end'],
            'end': mouth_lm['end'] + offset
        })
        new_mouth_lms.append({
            'ipa_code': config.SILENT_IPA_CODE
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

        return mouth_lms

    def _compute_mouth_lms(self, forced_aligner_data, duration):
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

        if not_found:
            mouth_lms.append({
                'ipa_code': self.NOT_FOUND_IN_AUDIO,
                'start': mouth_start,
                'end': duration
            })

        return mouth_lms

    def _execute_forced_aligner(self, audio_file_path, text_file_path):
        files = {
            'audio': open(audio_file_path, 'rb'),
            'transcript': open(text_file_path, 'rb')
        }
        res = requests.post(config.FORCED_ALIGNER_URL, files=files)
        return res.json()

    def _get_mouth_lms_points(self, model_name):
        file_path = config.MOUTH_LMS_FILE_PATH.format(model_name)
        with open(file_path) as f:
            data = f.read()
        return json.loads(data)

    def _interpolate_mouth_lms(self, mouth_lms):
        tmp_start = None
        int_mouth_lms = []
        oov_frames = {}
        num = len(mouth_lms)

        for i, mouth_lm in enumerate(mouth_lms):
            if i + 1 == num:
                break

            if not tmp_start:
                start_frame = round(mouth_lm['start'] * self.FPS)
            else:
                start_frame = tmp_start
            end_frame = round(mouth_lm['end'] * self.FPS)

            if end_frame - start_frame <= 1:
                tmp_start = start_frame
                continue
            tmp_start = None

            ipa_code = mouth_lm['ipa_code']
            next_ipa_code = mouth_lms[i + 1]['ipa_code']

            int_mouth_lms, oov_frames = self._interpolate_mouth_points(int_mouth_lms, oov_frames,
                                                                       start_frame, end_frame,
                                                                       ipa_code, next_ipa_code)

        return int_mouth_lms, oov_frames

    def _interpolate_mouth_points(self, int_mouth_lms, oov_frames, start_frame, end_frame,
                                  ipa_code, next_ipa_code):
        for i in range(start_frame, end_frame):
            percentage = float(i - start_frame) / float(end_frame - start_frame - 1)

            if percentage < config.MIN_PERCENTAGE:
                percentage /= config.PERCENTAGE_CLIP

            mouth_points = []
            for a in range(self.num_mouth_points):
                # Check if ipa code exists
                if ipa_code in [self.NOT_FOUND_IN_AUDIO, self.OUT_OF_VOCABULARY]:
                    ipa_code = config.NOT_FOUND_IPA_CODE
                    oov_frames[start_frame] = end_frame

                x, y = self.mouth_lms_points.get(ipa_code)[a]
                # Check if ipa code exists
                if next_ipa_code in [self.NOT_FOUND_IN_AUDIO, self.OUT_OF_VOCABULARY]:
                    next_ipa_code = config.NOT_FOUND_IPA_CODE

                target_x, target_y = self.mouth_lms_points.get(next_ipa_code)[a]
                # Calculate interpolated points
                int_x = x + ((target_x - x) * percentage)
                int_y = y + ((target_y - y) * percentage)
                mouth_points.append((int_x, int_y))

            int_mouth_lms.insert(i, {
                'ipa_code': ipa_code,
                'mouth_points': mouth_points
            })

        return int_mouth_lms, oov_frames

    def _save_text(self, text):
        with open(config.TEXT_FILE_PATH, 'w') as f:
            f.write(text)

    def generate(self, audio_file_path, text, duration):
        self._save_text(text)
        forced_aligner_data = self._execute_forced_aligner(audio_file_path,
                                                           config.TEXT_FILE_PATH)
        mouth_lms = self._compute_mouth_lms(forced_aligner_data, duration)
        mouth_lms = self._adjust_lms(mouth_lms)
        mouth_lms = self._check_mouth_lms(mouth_lms)
        mouth_lms, oov_frames = self._interpolate_mouth_lms(mouth_lms)
        return forced_aligner_data, mouth_lms, oov_frames
