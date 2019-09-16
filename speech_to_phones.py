import math
import requests

from config import *


class MouthLandmarksGenerator(object):

    def __init__(self):

    def _add_silent_lms(self, mouth_lms):
        old_mouth_end = 0
        new_mouth_lms = []

        for mouth_lm in mouth_lms:
            mouth_start = mouth_lm['start']
            # Checks if there is a "gap"/"silence" between mouths landmarks.
            # If there is a gap, then add "silent" IPA.
            if mouth_start - old_mouth_end > 0:
                new_mouth_lms.append({
                    'ipa_code': self.SILENT_IPA_CODE,
                    'start': old_mouth_end,
                    'end': mouth_start
                })
            old_mouth_end = mouth_lm['end']
            new_mouth_lms.append(mouth_lm)

        # Add ending mouth position
        new_mouth_lms.append({
            'ipa_code': self.SILENT_IPA_CODE,
            'start': old_mouth_end,
            'end': old_mouth_end + self.OFFSET_END
        })

        return new_mouth_lms

    def _compute_mouth_lms(self, forced_aligner_data):
        mouth_lms = []
        for word in forced_aligner_data['words']:
            mouth_start = word['start']
            mouth_end = mouth_start
            for phone in word['phones']:
                # Extract IPA code
                phone_name = phone['phone']
                ipa_code = phone_name.split('_')[0].upper()
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
        res = requests.post(self.FORCED_ALIGNER_URL, files=files)
        return res.json()

    def _interpolate_mouth_lms(self, mouth_lms):
        int_mouth_lms = []
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
            int_mouth_lms = self._interpolate_mouth_points(int_mouth_lms, start_frame, end_frame,
                                                           ipa_code, next_ipa_code)

        return int_mouth_lms

    def _interpolate_mouth_points(self, int_mouth_lms, start_frame, end_frame, ipa_code,
                                  next_ipa_code):
        for i in range(start_frame, end_frame):
            percentage = float(i - start_frame + 1) / float(end_frame - start_frame)
            print('percentage:', percentage)
            if percentage < self.MIN_PERCENTAGE:
                percentage /= self.PERCENTAGE_CLIP
            print('percentage2:', percentage)
            mouth_points = []
            for a in range(self.num_mouth_points):
                # Check if ipa code exists
                if ipa_code not in self.mouth_lms_points:
                    print('ipa_code:', ipa_code)
                    raise
                x, y = self.mouth_lms_points.get(ipa_code)[a]
                # Check if ipa code exists
                if next_ipa_code not in self.mouth_lms_points:
                    print('ipa_code:', ipa_code)
                    raise
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

        return int_mouth_lms

