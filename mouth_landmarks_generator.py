import config
import json
import random
import requests

from g2p_en import G2p


class MouthLandmarksGenerator(object):

    CASE_G2P = 'inferred-g2p'
    G2P = G2p()
    NOT_FOUND_IN_AUDIO = 'not-found-in-audio'
    UNKNOWN = '<unk>'

    def __init__(self, model_name):
        self.FPS = float(config.FPS)
        self.mouth_lms_points = self._get_mouth_lms_points(model_name)
        # All mouth landmarks have the same number of points.
        # Here we can use the default ipa code to obtain the number of mouth points.
        self.num_mouth_points = len(self.mouth_lms_points[config.NOT_FOUND_IPA_CODE])

    def _adjust_lms(self, mouth_lms):
        prev_mouth = None
        new_mouth_lms = []

        for i, mouth_lm in enumerate(mouth_lms):
            mouth_start = mouth_lm['start']
            # Checks if there is a "gap"/"silence" between initial mouths landmarks
            if i == 0 and mouth_start > config.INIT_MOUTH_DURATION:
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
            elif i != 0 and mouth_start - prev_mouth['end'] > config.MAX_DURATION_BETWEEN_LMS:
                offset = (mouth_start - prev_mouth['end']) / 2
                new_mouth_lms.append({
                    'ipa_code': config.REST_IPA_CODE,
                    'start': prev_mouth['end'],
                    'end': mouth_start - offset
                })
                new_mouth_lms.append({
                    'ipa_code': config.REST_IPA_CODE,
                    'start': mouth_start - offset,
                    'end': mouth_start
                })
            # Checks if there is a small "gap"/"silence" between mouths landmarks
            elif i != 0 and mouth_start - prev_mouth['end'] > 0:
                prev_mouth['end'] = mouth_start

            new_mouth_lms.append(mouth_lm)
            prev_mouth = mouth_lm

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

    def _check_forced_aligner_g2p(self, forced_aligner_data):
        for token in forced_aligner_data['words']:
            if token['case'] == self.CASE_G2P:
                duration = token['end'] - token['start']
                word = token['word']
                phones = self.G2P(word)
                num_phones = len(phones)

                token['phones'] = []
                for phone in phones:
                    # Remove numbers from phone, for example 'AY1' to 'AY'
                    phone = ''.join(p for p in phone if not p.isdigit())
                    token['phones'].append({
                        'duration': duration / num_phones,
                        'phone': phone
                    })

        return forced_aligner_data

    def _check_forced_aligner_timing(self, forced_aligner_data, init_duration, duration):
        tmp_time = None
        tokens = forced_aligner_data['words']
        num_tokens = len(tokens)

        for i, token in enumerate(tokens):
            prev_token = tokens[i - 1]

            if token['case'] == self.CASE_G2P:
                continue

            if token['case'] == self.NOT_FOUND_IN_AUDIO \
                or token['alignedWord'] == self.UNKNOWN:
                if i == 0:
                    tmp_time = init_duration
                    continue

                elif i + 1 == num_tokens:
                    token['case'] = self.CASE_G2P

                    if tmp_time is None:
                        token['start'] = prev_token['end']
                        token['end'] = duration
                    else:
                        found_idx = None
                        for a in reversed(range(i)):
                            prev_token = tokens[a]
                            if 'end' in prev_token:
                                found_idx = a
                                break

                        t_duration = (duration - tmp_time) / (i - found_idx)
                        for a in range(found_idx + 1, i + 1):
                            tokens[a]['case'] = self.CASE_G2P
                            tokens[a]['start'] = tmp_time
                            tokens[a]['end'] = tmp_time + t_duration
                            tmp_time = tokens[a]['end']

                        tmp_time = None

                    continue

                elif tmp_time is None:
                    tmp_time = prev_token['end']
                    continue

                else:
                    found_idx = None
                    for a in range(i + 1, num_tokens + 1):
                        next_token = tokens[a]
                        if 'start' in next_token:
                            found_idx = a
                            break

                    t_duration = (tokens[found_idx]['start'] - tmp_time) / (found_idx - i + 1)
                    for a in range(i - 1, found_idx):
                        tokens[a]['case'] = self.CASE_G2P
                        tokens[a]['start'] = tmp_time
                        tokens[a]['end'] = tmp_time + t_duration
                        tmp_time = tokens[a]['end']

                    tmp_time = None
                    continue

            elif tmp_time is not None:
                prev_token['case'] = self.CASE_G2P
                prev_token['end'] = token['start']
                prev_token['start'] = tmp_time
                tmp_time = None

        return forced_aligner_data

    def _check_mouth_lms(self, mouth_lms):
        # Fixes issue with Gentle's output
        num = len(mouth_lms)
        for i, mouth_lm in enumerate(mouth_lms):
            if i + 1 == num:
                break
            if i > 0 and prev_mouth['end'] > mouth_lm['start']:
                prev_mouth['end'] = mouth_lm['start']
            prev_mouth = mouth_lm

        # Skip landmarks
        new_mouth_lms = []
        tmp_mouth_lms = None
        for i, mouth_lm in enumerate(mouth_lms):
            if tmp_mouth_lms is not None:
                mouth_lm['start'] = tmp_mouth_lms['start']
                tmp_mouth_lms = None

            if i + 1 == len(mouth_lms):
                new_mouth_lms.append(mouth_lm)
                break

            if mouth_lm['end'] - mouth_lm['start'] < config.MIN_PHONE_DURATION:
                tmp_mouth_lms = mouth_lm
                continue

            new_mouth_lms.append(mouth_lm)

        return new_mouth_lms

    def _compute_mouth_lms(self, forced_aligner_data):
        mouth_lms = []

        for word in forced_aligner_data['words']:
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
        res = requests.post(config.FORCED_ALIGNER_URL, files=files)
        return res.json()

    def _get_mouth_lms_points(self, model_name):
        file_path = config.MOUTH_LMS_FILE_PATH.format(model_name)
        with open(file_path) as f:
            data = f.read()
        return json.loads(data)

    def _interpolate_mouth_lms(self, mouth_lms, min_percentage, percentage_clip):
        int_mouth_lms = []
        oov_frames = {}
        num = len(mouth_lms)

        for i, mouth_lm in enumerate(mouth_lms):
            if i + 1 == num:
                break

            start_frame = round(mouth_lm['start'] * self.FPS)
            end_frame = round(mouth_lm['end'] * self.FPS)

            ipa_code = mouth_lm['ipa_code']
            next_ipa_code = mouth_lms[i + 1]['ipa_code']

            int_mouth_lms, oov_frames = self._interpolate_mouth_points(int_mouth_lms, oov_frames,
                                                                       start_frame, end_frame,
                                                                       ipa_code, next_ipa_code,
                                                                       min_percentage,
                                                                       percentage_clip)

        return int_mouth_lms, oov_frames

    def _interpolate_mouth_points(self, int_mouth_lms, oov_frames, start_frame, end_frame,
                                  ipa_code, next_ipa_code, min_percentage, percentage_clip):
        for i in range(start_frame, end_frame):
            percentage = float(i - start_frame + 1) / float(end_frame - start_frame)

            if percentage < min_percentage:
                percentage /= percentage_clip

            mouth_points = []
            for a in range(self.num_mouth_points):
                x, y = self.mouth_lms_points[ipa_code][a]
                target_x, target_y = self.mouth_lms_points[next_ipa_code][a]
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

    def generate(self, audio_file_path, text, init_duration, duration,
                 min_percentage, percentage_clip):
        self._save_text(text)
        forced_aligner_data = self._execute_forced_aligner(audio_file_path,
                                                           config.TEXT_FILE_PATH)
        forced_aligner_data = self._check_forced_aligner_timing(forced_aligner_data,
                                                                init_duration,
                                                                duration)
        forced_aligner_data = self._check_forced_aligner_g2p(forced_aligner_data)
        mouth_lms = self._compute_mouth_lms(forced_aligner_data)
        mouth_lms = self._adjust_lms(mouth_lms)
        mouth_lms = self._check_mouth_lms(mouth_lms)
        mouth_lms, oov_frames = self._interpolate_mouth_lms(mouth_lms,
                                                            min_percentage,
                                                            percentage_clip)
        return forced_aligner_data, mouth_lms, oov_frames
