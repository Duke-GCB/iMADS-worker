import yaml

TEST_CONFIG_YAML = """- assembly: hg38
  author_identifier: AA
  cores:
  - GGAA
  - GGAT
  filter_threshold: 0.1
  kmers:
  - 1
  - 2
  - 3
  model_filenames:
  - model1.model
  - model2.model
  protein: ABC1
  serial_number: '9876'
  slope_intercept: false
  track_filename: hg38-9876-ABC1.bb
  width: 20
  transform: False
"""

CONFIG_2X2 = yaml.safe_load(TEST_CONFIG_YAML)[0]
CONFIG_1X3 = {'cores': ['AAAA', 'CCCC', 'TTTT'],
              'kmers': [1],
              'model_filenames': ['model'],
              'width': 20,}
