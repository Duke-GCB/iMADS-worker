import tempfile
from unittest import TestCase

import test_data
from predict_service.cwljob import PredictionsCwlJobGenerator


class CwlJobGeneratorTestCase(TestCase):
    def test_model_dict(self):
        g = PredictionsCwlJobGenerator(test_data.CONFIG_2X2, 'seq.fa', '/models')
        self.assertIsNotNone(g.job)
        self.assertNotIn('models', test_data.CONFIG_2X2, 'test dataset should have model_filenames')
        self.assertIn('models', g.job, 'generated job dict should just have models')
        self.assertEqual(g.job['sequence'], {'class': 'File', 'path': 'seq.fa'}, 'job should have sequence file object')

    def test_writes_json(self):
        g = PredictionsCwlJobGenerator(test_data.CONFIG_2X2, 'seq.fa', '/models')
        output_file = tempfile.NamedTemporaryFile("w", encoding="utf8")
        self.assertEqual(output_file.tell(), 0)
        g.write_json(output_file)
        self.assertNotEqual(output_file.tell(), 0, 'write_json should have written to the file')

    def test_includes_output_filename(self):
        g = PredictionsCwlJobGenerator(test_data.CONFIG_2X2, 'seq.fa', '/models', 'myfile.out')
        self.assertIn('output_filename', g.job)
        self.assertEqual(g.job['output_filename'], 'myfile.out')

    def test_omits_output_filename(self):
        g = PredictionsCwlJobGenerator(test_data.CONFIG_2X2, 'seq.fa', '/models')
        self.assertNotIn('output_filename', g.job)

    def test_matrixes_models(self):
        g = PredictionsCwlJobGenerator(test_data.CONFIG_1X3, 'seq.fa', '/models')
        self.assertEqual(len(test_data.CONFIG_1X3['model_filenames']), 1)
        self.assertEqual(len(test_data.CONFIG_1X3['cores']), 3)
        self.assertEqual(len(g.job['models']), 3)
        self.assertEqual(len(g.job['cores']), 3)

    def test_fails_without_params(self):
        with self.assertRaises(ValueError):
            PredictionsCwlJobGenerator(None, 'seq.fa', '/models')
        with self.assertRaises(ValueError):
            PredictionsCwlJobGenerator({}, None, '/models')
        with self.assertRaises(ValueError):
            PredictionsCwlJobGenerator({}, 'seq.fa', None)
