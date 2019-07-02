import shutil
import tempfile
from unittest import TestCase

from predict_service.runner import PredictionRunner, RunnerException
from mock import Mock, patch

class PredictionRunnerTestCase(TestCase):
    sequence = 'predict_service/tests/test_sequence.fa'
    model = 'ABCD_1234(AB)'
    config = 'predict_service/tests/test_config.yaml'
    models_dir = '/models'

    def setUp(self):
        self.output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.output_dir)

    def test_writes_json_order(self):
        p = PredictionRunner(self.sequence, self.model, self.config, self.models_dir, self.output_dir)
        p.write_json_order()

    def test_fails_with_missing_sequence(self):
        with self.assertRaises(ValueError):
            PredictionRunner(None, self.model, self.config, self.models_dir, self.output_dir)

    def test_fails_with_missing_model(self):
        with self.assertRaises(ValueError):
            PredictionRunner(self.sequence, None, self.config, self.models_dir, self.output_dir)

    def test_fails_with_missing_config(self):
        with self.assertRaises(ValueError):
            PredictionRunner(self.sequence, self.model, None, self.models_dir, self.output_dir)

    def test_generates_order_file_name(self):
        p = PredictionRunner(self.sequence, self.model, self.config, self.models_dir, self.output_dir)
        order_file_name = p.order_file_name
        self.assertIn('.json', order_file_name)
        self.assertIn(self.model, order_file_name)

    def test_generates_ooutput_file_name(self):
        p = PredictionRunner(self.sequence, self.model, self.config, self.models_dir, self.output_dir)
        output_file_name = p.output_file_name
        self.assertIn('.bed', output_file_name)
        self.assertIn(self.model, output_file_name)

    @patch('predict_service.runner.cwl_main')
    def test_runs_cwltool_gets_output(self, mock_cwl_main):
        p = PredictionRunner(self.sequence, self.model, self.config, self.models_dir, self.output_dir)
        def side_effect(args, stdout, stderr):
          print('{"predictions":{"path": "/preds.bed","class": "File","size": 124}}', file=stdout)
          return 0
        mock_cwl_main.side_effect = side_effect
        result = p.run()
        self.assertTrue(mock_cwl_main.called)
        self.assertEqual(result['path'], '/preds.bed')

    @patch('predict_service.runner.cwl_main')
    def test_handles_cwltool_failures(self, mock_cwl_main):
        p = PredictionRunner(self.sequence, self.model, self.config, self.models_dir, self.output_dir)
        def side_effect(args, stdout, stderr):
          print('error in cwl_main', file=stderr)
          return 1
        mock_cwl_main.side_effect = side_effect
        with self.assertRaises(RunnerException):
          p.run()
          self.assertTrue(mock_cwl_main.called)
