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
	@patch('config.FPS', 1.0)
	def test_start_gap(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'case': 'success',
					'end': 6.0,
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
					'start': 2.0,
					'word': 'Hi'
				}
			]
		}
		mock_uniform.return_value = 2.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, None)

		assert mouth_lms == [
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(52.0, 581.0)]},
			{'ipa_code': 'HH', 'mouth_points': [(52.0, 581.0)]},
			{'ipa_code': 'HH', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 2.0)
	@patch('config.MIN_TIME_BETWEEN_LMS', 0.5)
	def test_big_inbetween_gap(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
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
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, None)

		assert mouth_lms == [
			{'ipa_code': 'HH', 'mouth_points': [(52.0, 581.0)]},
			{'ipa_code': 'HH', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'AY', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(57.0, 583.0)]},
			{'ipa_code': 'EH', 'mouth_points': [(57.0, 583.0)]},
			{'ipa_code': 'EH', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 2.0)
	@patch('config.MIN_TIME_BETWEEN_LMS', 2)
	def test_small_inbetween_gap(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
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
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, None)

		assert mouth_lms == [
			{'ipa_code': 'M',  'mouth_points': [(63.0, 586.0)]},
			{'ipa_code': 'M',  'mouth_points': [(62.333333333333336, 583.3333333333334)]},
			{'ipa_code': 'M',  'mouth_points': [(61.666666666666664, 580.6666666666666)]},
			{'ipa_code': 'M',  'mouth_points': [(61.0, 578.0)]},
			{'ipa_code': 'IY', 'mouth_points': [(61.0, 578.0)]},
			{'ipa_code': 'IY', 'mouth_points': [(59.0, 584.0)]},
			{'ipa_code': 'D',  'mouth_points': [(59.0, 584.0)]},
			{'ipa_code': 'D',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(60.8, 583.2)]},
			{'ipa_code': 'P',  'mouth_points': [(60.6, 582.4)]},
			{'ipa_code': 'P',  'mouth_points': [(60.4, 581.6)]},
			{'ipa_code': 'P',  'mouth_points': [(60.2, 580.8)]},
			{'ipa_code': 'P',  'mouth_points': [(60.0, 580.0)]},
			{'ipa_code': 'ER', 'mouth_points': [(60.0, 580.0)]},
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
	def test_not_found_in_audio(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'case': 'not-found-in-audio',
					'word': 'Hi'
				},
				{
					'case': 'success',
					'end': 4.0,
					'phones': [
						{
							'duration': 2.0,
							'phone': 'ao_I'
						},
					],
					'start': 2.0,
					'word': 'you'
				}
			]
		}
		mock_uniform.return_value = 2.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, None)

		assert mouth_lms == [
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 581.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 580.6666666666666)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 580.3333333333334)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 580.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(62.0, 580.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(61.666666666666664, 581.3333333333334)]},
			{'ipa_code': 'AO', 'mouth_points': [(61.333333333333336, 582.6666666666666)]},
			{'ipa_code': 'AO', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {
			0: 4
		}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 1.0)
	def test_multiple_ini_not_found_in_audio(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'case': 'not-found-in-audio',
					'word': 'Hi'
				},
				{
					'case': 'not-found-in-audio',
					'word': 'you'
				},
				{
					'case': 'success',
					'end': 8.0,
					'phones': [
						{
							'duration': 2.0,
							'phone': 'ao_I'
						},
					],
					'start': 6.0,
					'word': 'there'
				}
			]
		}
		mock_uniform.return_value = 2.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, None)

		assert mouth_lms == [
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 581.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 580.8)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 580.6)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 580.4)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 580.2)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 580.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(62.0, 580.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {
			0: 6
		}

	@patch('random.uniform')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._save_text')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._execute_forced_aligner')
	@patch('mouth_landmarks_generator.MouthLandmarksGenerator._get_mouth_lms_points')
	@patch('config.FPS', 1.0)
	def test_multiple_end_not_found_in_audio(self, mock_get_mouth_lms, mock_execute_fa, mock_save, mock_uniform):
		mock_get_mouth_lms.return_value = self.MOUTH_LMS
		mock_execute_fa.return_value = {
			'words': [
				{
					'case': 'not-found-in-audio',
					'word': 'Hi'
				},
				{
					'case': 'success',
					'end': 5.0,
					'phones': [
						{
							'duration': 2.0,
							'phone': 'ao_I'
						},
					],
					'start': 3.0,
					'word': 'there'
				},
				{
					'case': 'not-found-in-audio',
					'word': 'you'
				}
			]
		}
		mock_uniform.return_value = 3.0

		from mouth_landmarks_generator import MouthLandmarksGenerator
		_, mouth_lms, oov_frames = MouthLandmarksGenerator(None).generate(None, None, 8)

		assert mouth_lms == [
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 581.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 580.5)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 580.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(62.0, 580.0)]},
			{'ipa_code': 'AO', 'mouth_points': [(62.0, 581.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(62.0, 581.0)]},
			{'ipa_code': 'AA', 'mouth_points': [(61.5, 582.5)]},
			{'ipa_code': 'AA', 'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]},
			{'ipa_code': 'P',  'mouth_points': [(61.0, 584.0)]}
		]
		assert oov_frames == {
			0: 3,
			5: 8
		}
