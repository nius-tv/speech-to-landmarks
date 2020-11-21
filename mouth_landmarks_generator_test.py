import config
import pytest
# @pytest.mark.only
import unittest

from unittest.mock import patch


class TestMouthLandmarksGenerator(unittest.TestCase):

	MOUTH_LMS = {
		'AA': [[62.0, 581.0]], 'AE': [[59.0, 588.0]], 'AH': [[57.0, 588.0]], 'AO': [[62.0, 580.0]],
		'AW': [[58.0, 581.0]], 'AY': [[60.0, 580.0]], 'B':  [[63.0, 590.0]], 'CH': [[59.0, 585.0]],
		'D':  [[59.0, 584.0]], 'DH': [[56.0, 586.0]], 'EH': [[57.0, 583.0]], 'ER': [[60.0, 580.0]],
		'EY': [[56.0, 581.0]], 'F':  [[55.0, 572.0]], 'G':  [[49.0, 581.0]], 'HH': [[52.0, 581.0]],
		'IH': [[54.0, 585.0]], 'IY': [[61.0, 578.0]], 'JH': [[60.0, 585.0]], 'K':  [[55.0, 582.0]],
		'L':  [[58.0, 587.0]], 'M':  [[63.0, 586.0]], 'N':  [[61.0, 583.0]], 'NG': [[59.0, 582.0]],
		'OW': [[60.0, 588.0]], 'OY': [[59.0, 582.0]], 'P':  [[61.0, 584.0]], 'R':  [[59.0, 584.0]],
		'S':  [[55.0, 576.0]], 'SH': [[59.0, 590.0]], 'T':  [[53.0, 584.0]], 'TH': [[53.0, 586.0]],
		'UH': [[58.0, 583.0]], 'UW': [[60.0, 579.0]], 'V':  [[64.0, 581.0]], 'W':  [[59.0, 579.0]],
		'Y':  [[57.0, 586.0]], 'Z':  [[55.0, 593.0]], 'ZH': [[58.0, 589.0]]
	}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 2.0)
	@patch('config.MAX_DURATION_BETWEEN_LMS', 0.5)
	@patch('config.REST_IPA_CODE', 'P')
	def test_big_inbetween_gap(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': 'Hi',
					'case': 'success',
					'end': 2.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'hh_B'
						},
						{
							'duration': 1.0,
							'phone': 'ay_E'
						}
					],
					'start': 0.0,
					'word': 'Hi'
				},
				{
					'alignedWord': 'E',
					'case': 'success',
					'end': 4.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'eh_y'
						}
					],
					'start': 3.0,
					'word': 'E'
				}
			]
		}
		mock_uniform.return_value = 1.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, None, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'HH', 'mouth_points': [(56.0, 580.5)]},
			{'ipa_code': 'HH', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(60.5, 582.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(57.0, 583.0)]},
			{'ipa_code': 'EH', 'mouth_points': [(59.0, 583.5)]},
			{'ipa_code': 'EH', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 1.0)
	@patch('config.REST_IPA_CODE', 'P')
	def test_ini_end_not_found_in_audio(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': 'Hi',
					'case': 'not-found-in-audio',
					'word': 'Hi'
				},
				{
					'alignedWord': 'there',
					'case': 'success',
					'end': 5.0,
					'phones': [
						{
							'duration': 2.0,
							'phone': 'ao_I'
						}
					],
					'start': 3.0,
					'word': 'there'
				},
				{
					'alignedWord': 'you',
					'case': 'not-found-in-audio',
					'word': 'you'
				}
			]
		}
		mock_uniform.return_value = 3.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, 8, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'HH', 'mouth_points': [(56.0, 580.5)]},
			{'ipa_code': 'HH', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(62.0, 580.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(59.5, 583.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(57.0, 586.0)]},
			{'ipa_code': 'Y',  'mouth_points': [(60.0, 579.0)]},
			{'ipa_code': 'UW', 'mouth_points': [(60.5, 581.5)]},
			{'ipa_code': 'UW', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 1.0)
	@patch('config.INIT_MOUTH_DURATION', 3)
	@patch('config.REST_IPA_CODE', 'P')
	def test_ini_gap(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': 'Hi',
					'case': 'success',
					'end': 9.0,
					'phones': [
						{
							'duration': 2.0,
							'phone': 'hh_B'
						},
						{
							'duration': 2.0,
							'phone': 'ay_E'
						}
					],
					'start': 5.0,
					'word': 'Hi'
				}
			]
		}
		mock_uniform.return_value = 2.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, None, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(58.0, 583.0)]},
			{'ipa_code': 'P',  'mouth_points': [(55.0, 582.0)]},
			{'ipa_code': 'P',  'mouth_points': [(52.0, 581.0)]},
			{'ipa_code': 'HH', 'mouth_points': [(56.0, 580.5)]},
			{'ipa_code': 'HH', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(60.5, 582.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 1.0)
	@patch('config.REST_IPA_CODE', 'P')
	def test_multiple_end_not_found_in_audio(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': 'Hi',
					'case': 'success',
					'end': 4.0,
					'phones': [
						{
							'duration': 2.0,
							'phone': 'HH_i'
						}
					],
					'start': 2.0,
					'word': 'Hi'
				},
				{
					'alignedWord': 'there',
					'case': 'not-found-in-audio',
					'word': 'there'
				},
				{
					'alignedWord': 'you',
					'case': 'not-found-in-audio',
					'word': 'you'
				}
			]
		}
		mock_uniform.return_value = 2.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, 8, 0, 0)

		assert mouth_lms == [
			{"ipa_code": 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'HH', 'mouth_points': [(54.0, 583.5)]},
			{'ipa_code': 'HH', 'mouth_points': [(56.0, 586.0)]},
			{'ipa_code': 'DH', 'mouth_points': [(57.0, 583.0)]},
			{'ipa_code': 'R',  'mouth_points': [(57.0, 586.0)]},
			{'ipa_code': 'Y',  'mouth_points': [(60.0, 579.0)]},
			{'ipa_code': 'UW', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 1.0)
	@patch('config.REST_IPA_CODE', 'P')
	def test_multiple_ini_not_found_in_audio(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': 'Hi',
					'case': 'not-found-in-audio',
					'word': 'Hi'
				},
				{
					'alignedWord': 'you',
					'case': 'not-found-in-audio',
					'word': 'you'
				},
				{
					'alignedWord': 'there',
					'case': 'success',
					'end': 8.0,
					'phones': [
						{
							'duration': 2.0,
							'phone': 'ao_I'
						}
					],
					'start': 6.0,
					'word': 'there'
				}
			]
		}
		mock_uniform.return_value = 2.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, None, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'HH', 'mouth_points': [(56.0, 580.5)]},
			{'ipa_code': 'HH', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(57.0, 586.0)]},
			{'ipa_code': 'Y',  'mouth_points': [(60.0, 579.0)]},
			{'ipa_code': 'UW', 'mouth_points': [(61.0, 579.5)]},
			{'ipa_code': 'UW', 'mouth_points': [(62.0, 580.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(61.5, 582.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 2.0)
	@patch('config.REST_IPA_CODE', 'P')
	def test_multiple_not_found_in_audio(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': 'Hi',
					'case': 'not-found-in-audio',
					'word': 'Hi'
				},
				{
					'alignedWord': 'there',
					'case': 'success',
					'end': 3.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'iy_I'
						}
					],
					'start': 2.0,
					'word': 'there'
				},
				{
					'alignedWord': 'yes',
					'case': 'not-found-in-audio',
					'word': 'yes'
				},
				{
					'alignedWord': 'no',
					'case': 'not-found-in-audio',
					'word': 'no'
				},
				{
					'alignedWord': 'maybe',
					'case': 'not-found-in-audio',
					'word': 'maybe'
				},
				{
					'alignedWord': 'maybe',
					'case': 'success',
					'end': 7.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'uw_I'
						}
					],
					'start': 6.0,
					'word': 'maybe'
				}
			]
		}
		mock_uniform.return_value = 1.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, None, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'HH', 'mouth_points': [(56.0, 580.5)]},
			{'ipa_code': 'HH', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(60.5, 579.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(61.0, 578.0)]},
			{'ipa_code': 'IY', 'mouth_points': [(59.0, 582.0)]},
			{'ipa_code': 'IY', 'mouth_points': [(57.0, 586.0)]},
			{'ipa_code': 'Y',  'mouth_points': [(57.0, 583.0)]},
			{'ipa_code': 'S',  'mouth_points': [(61.0, 583.0)]},
			{'ipa_code': 'N',  'mouth_points': [(60.0, 588.0)]},
			{'ipa_code': 'OW', 'mouth_points': [(63.0, 586.0)]},
			{'ipa_code': 'EY', 'mouth_points': [(63.0, 590.0)]},
			{'ipa_code': 'B',  'mouth_points': [(61.0, 578.0)]},
			{'ipa_code': 'UW', 'mouth_points': [(60.5, 581.5)]},
			{'ipa_code': 'UW', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 2.0)
	@patch('config.REST_IPA_CODE', 'P')
	def test_not_found_in_audio(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': 'Hi',
					'case': 'not-found-in-audio',
					'word': 'Hi'
				},
				{
					'alignedWord': 'you',
					'case': 'success',
					'end': 4.0,
					'phones': [
						{
							'duration': 2.0,
							'phone': 'ao_I'
						}
					],
					'start': 2.0,
					'word': 'you'
				}
			]
		}
		mock_uniform.return_value = 2.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 1, None, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'HH', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(62.0, 580.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(61.75, 581.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(61.5, 582.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(61.25, 583.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 10.0)
	@patch('config.REST_IPA_CODE', 'P')
	def test_percentage(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = {
			'AA': [[0.0, 0.0]],
			'AE': [[100.0, 100.0]],
			'P':  [[200.0, 200.0]]
		}
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': '',
					'case': 'success',
					'end': 1.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'aa_i'
						}
					],
					'start': 0.0,
				},
				{
					'alignedWord': '',
					'case': 'success',
					'end': 2.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'ae_i'
						}
					],
					'start': 1.0,
				}
			]
		}
		mock_uniform.return_value = 1.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, None, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'AA', 'mouth_points': [(10.0, 10.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(20.0, 20.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(30.0, 30.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(40.0, 40.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(50.0, 50.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(60.0, 60.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(70.0, 70.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(80.0, 80.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(90.0, 90.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(100.0, 100.0)]},
			{'ipa_code': 'AE', 'mouth_points': [(108.33333333333333, 108.33333333333333)]},
			{'ipa_code': 'AE', 'mouth_points': [(116.66666666666666, 116.66666666666666)]},
			{'ipa_code': 'AE', 'mouth_points': [(125.0, 125.0)]},
			{'ipa_code': 'AE', 'mouth_points': [(133.33333333333331, 133.33333333333331)]},
			{'ipa_code': 'AE', 'mouth_points': [(141.66666666666669, 141.66666666666669)]},
			{'ipa_code': 'AE', 'mouth_points': [(150.0, 150.0)]},
			{'ipa_code': 'AE', 'mouth_points': [(158.33333333333334, 158.33333333333334)]},
			{'ipa_code': 'AE', 'mouth_points': [(166.66666666666666, 166.66666666666666)]},
			{'ipa_code': 'AE', 'mouth_points': [(175.0, 175.0)]},
			{'ipa_code': 'AE', 'mouth_points': [(183.33333333333334, 183.33333333333334)]},
			{'ipa_code': 'AE', 'mouth_points': [(191.66666666666666, 191.66666666666666)]},
			{'ipa_code': 'AE', 'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]}
		]
		assert oov_frames == {}

		# Test MIN_PERCENTAGE and 
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, None, 0.75, 5)

		assert mouth_lms == [
			{'ipa_code': 'AA', 'mouth_points': [(2.0, 2.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(4.0, 4.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(6.0, 6.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(8.0, 8.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(10.0, 10.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(12.0, 12.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(13.999999999999998, 13.999999999999998)]},
			{'ipa_code': 'AA', 'mouth_points': [(80.0, 80.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(90.0, 90.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(100.0, 100.0)]},
			{'ipa_code': 'AE', 'mouth_points': [(101.66666666666667, 101.66666666666667)]},
			{'ipa_code': 'AE', 'mouth_points': [(103.33333333333333, 103.33333333333333)]},
			{'ipa_code': 'AE', 'mouth_points': [(105.0, 105.0)]},
			{'ipa_code': 'AE', 'mouth_points': [(106.66666666666667, 106.66666666666667)]},
			{'ipa_code': 'AE', 'mouth_points': [(108.33333333333333, 108.33333333333333)]},
			{'ipa_code': 'AE', 'mouth_points': [(110.0, 110.0)]},
			{'ipa_code': 'AE', 'mouth_points': [(111.66666666666667, 111.66666666666667)]},
			{'ipa_code': 'AE', 'mouth_points': [(113.33333333333333, 113.33333333333333)]},
			{'ipa_code': 'AE', 'mouth_points': [(175.0, 175.0)]},
			{'ipa_code': 'AE', 'mouth_points': [(183.33333333333334, 183.33333333333334)]},
			{'ipa_code': 'AE', 'mouth_points': [(191.66666666666666, 191.66666666666666)]},
			{'ipa_code': 'AE', 'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]},
			{'ipa_code': 'P',  'mouth_points': [(200.0, 200.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 1.0)
	@patch('config.MIN_PHONE_DURATION', 2)
	@patch('config.REST_IPA_CODE', 'P')
	def test_skip_landmarks(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': 'Hi',
					'case': 'success',
					'end': 2.0,
					'phones': [
						{
							'duration': 2.0,
							'phone': 'ay_B'
						},
						{
							'duration': 1.0,
							'phone': 'hh_B'
						}
					],
					'start': 2.0,
					'word': 'Hi'
				}
			]
		}
		mock_uniform.return_value = 2.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, None, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'P',  'mouth_points': [(60.5, 582.0)]},
			{'ipa_code': 'P',  'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(60.5, 582.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 2.0)
	@patch('config.MAX_DURATION_BETWEEN_LMS', 2)
	@patch('config.REST_IPA_CODE', 'P')
	def test_small_inbetween_gap(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': 'Hey',
					'case': 'success',
					'end': 1.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'm_B'
						}
					],
					'start': 0.0,
					'word': 'Hey'
				},
				{
					'alignedWord': 'you',
					'case': 'success',
					'end': 4.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'iy_I'
						},
						{
							'duration': 1.0,
							'phone': 'd_E'
						}
					],
					'start': 2.0,
					'word': 'you'
				},
				{
					'alignedWord': 'there',
					'case': 'success',
					'end': 8.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'er_B'
						}
					],
					'start': 7.0,
					'word': 'there'
				}
			]
		}
		mock_uniform.return_value = 2.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, None, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'M',  'mouth_points': [(62.5, 584.0)]},
			{'ipa_code': 'M',  'mouth_points': [(62.0, 582.0)]},
			{'ipa_code': 'M',  'mouth_points': [(61.5, 580.0)]},
			{'ipa_code': 'M',  'mouth_points': [(61.0, 578.0)]},
			{'ipa_code': 'IY', 'mouth_points': [(60.0, 581.0)]},
			{'ipa_code': 'IY', 'mouth_points': [(59.0, 584.0)]},
			{'ipa_code': 'D',  'mouth_points': [(60.0, 584.0)]},
			{'ipa_code': 'D',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(60.666666666666664, 582.6666666666666)]},
			{'ipa_code': 'P',  'mouth_points': [(60.333333333333336, 581.3333333333334)]},
			{'ipa_code': 'P',  'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'ER', 'mouth_points': [(60.5, 582.0)]},
			{'ipa_code': 'ER', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 2.0)
	@patch('config.REST_IPA_CODE', 'P')
	def test_unknown(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': '<unk>',
					'case': 'success',
					'word': 'Hi'
				},
				{
					'alignedWord': 'there',
					'case': 'success',
					'end': 3.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'iy_I'
						}
					],
					'start': 2.0,
					'word': 'there'
				},
				{
					'alignedWord': '<unk>',
					'case': 'success',
					'word': 'yes'
				},
				{
					'alignedWord': '<unk>',
					'case': 'success',
					'word': 'no'
				},
				{
					'alignedWord': 'maybe',
					'case': 'not-found-in-audio',
					'word': 'maybe'
				},
				{
					'alignedWord': 'maybe',
					'case': 'success',
					'end': 7.0,
					'phones': [
						{
							'duration': 1.0,
							'phone': 'uw_I'
						}
					],
					'start': 6.0,
					'word': 'maybe'
				}
			]
		}
		mock_uniform.return_value = 1.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, None, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'HH', 'mouth_points': [(56.0, 580.5)]},
			{'ipa_code': 'HH', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(60.5, 579.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(61.0, 578.0)]},
			{'ipa_code': 'IY', 'mouth_points': [(59.0, 582.0)]},
			{'ipa_code': 'IY', 'mouth_points': [(57.0, 586.0)]},
			{'ipa_code': 'Y',  'mouth_points': [(57.0, 583.0)]},
			{'ipa_code': 'S',  'mouth_points': [(61.0, 583.0)]},
			{'ipa_code': 'N',  'mouth_points': [(60.0, 588.0)]},
			{'ipa_code': 'OW', 'mouth_points': [(63.0, 586.0)]},
			{'ipa_code': 'EY', 'mouth_points': [(63.0, 590.0)]},
			{'ipa_code': 'B',  'mouth_points': [(61.0, 578.0)]},
			{'ipa_code': 'UW', 'mouth_points': [(60.5, 581.5)]},
			{'ipa_code': 'UW', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 2.0)
	@patch('config.REST_IPA_CODE', 'P')
	def test_unknown_not_found(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'alignedWord': '<unk>',
					'case': 'success',
					'end': 6,
					'phones': [
						{
							'duration': 1,
							'phone': 'oov_S'
						}
					],
					'start': 5,
					'word': 'EsS'
				},
				{
					'case': 'not-found-in-audio',
					'word': 'EmM'
				},
				{
					'case': 'not-found-in-audio',
					'word': 'EsS'
				},
				{
					'alignedWord': 'standard',
					'case': 'success',
					'end': 10,
					'phones': [
						{
							'duration': 1,
							'phone': 's_B'
						}
					],
					'start': 9,
					'word': 'standard'
				}
			]
		}
		mock_uniform.return_value = 1.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 0, None, 0, 0)

		assert mouth_lms == [
			{'ipa_code': 'EH', 'mouth_points': [(56.333333333333336, 580.6666666666666)]},
			{'ipa_code': 'EH', 'mouth_points': [(55.666666666666664, 578.3333333333334)]},
			{'ipa_code': 'EH', 'mouth_points': [(55.0, 576.0)]},
			{'ipa_code': 'S',  'mouth_points': [(55.666666666666664, 578.3333333333334)]},
			{'ipa_code': 'S',  'mouth_points': [(56.333333333333336, 580.6666666666666)]},
			{'ipa_code': 'S',  'mouth_points': [(57.0, 583.0)]},
			{'ipa_code': 'EH', 'mouth_points': [(59.0, 584.0)]},
			{'ipa_code': 'EH', 'mouth_points': [(61.0, 585.0)]},
			{'ipa_code': 'EH', 'mouth_points': [(63.0, 586.0)]},
			{'ipa_code': 'M',  'mouth_points': [(61.0, 585.0)]},
			{'ipa_code': 'M',  'mouth_points': [(59.0, 584.0)]},
			{'ipa_code': 'M',  'mouth_points': [(57.0, 583.0)]},
			{'ipa_code': 'EH', 'mouth_points': [(56.333333333333336, 580.6666666666666)]},
			{'ipa_code': 'EH', 'mouth_points': [(55.666666666666664, 578.3333333333334)]},
			{'ipa_code': 'EH', 'mouth_points': [(55.0, 576.0)]},
			{'ipa_code': 'S',  'mouth_points': [(55.0, 576.0)]},
			{'ipa_code': 'S',  'mouth_points': [(55.0, 576.0)]},
			{'ipa_code': 'S',  'mouth_points': [(55.0, 576.0)]},
			{'ipa_code': 'S',  'mouth_points': [(58.0, 580.0)]},
			{'ipa_code': 'S',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}
