cwlVersion: v1.0
class: Workflow
inputs:
  # Predictions
  sequence: File
  models1: File[]
  models2: File[]
  cores: string[]
  width: int
  kmers: int[]
  slope_intercept: boolean
  transform: boolean
  core_start: int?
  # Preferences
  tf1: string
  tf2: string
  tf1_threshold: float
  tf2_threshold: float
  output_filename: string
outputs:
  preferences:
    type: File
    outputSource: name_output/output
steps:
  predict1:
    run: predict-tf-binding.cwl
    in:
      sequence: sequence
      model: models1
      core: cores
      width: width
      kmers: kmers
      slope_intercept: slope_intercept
      transform: transform
      core_start: core_start
    out: [predictions]
  predict2:
    run: predict-tf-binding.cwl
    in:
      sequence: sequence
      model: models2
      core: cores
      width: width
      kmers: kmers
      slope_intercept: slope_intercept
      transform: transform
      core_start: core_start
    out: [predictions]
  combine1:
    run: combine.cwl
    in:
      input_files: predict1/predictions
    out: [combined]
  combine2:
    run: combine.cwl
    in:
      input_files: predict2/predictions
    out: [combined]
  preference:
    run: predict-tf-preference.cwl
    in:
      tf1: tf1
      tf1_bed_file: combine1/combined
      tf2: tf2
      tf2_bed_file: combine2/combined
    out: [preferences]
  filter:
    run: filter-tf-preference-threshold.cwl
    in:
      tf1_bed_file: combine1/combined
      tf1_threshold: tf1_threshold
      tf2_bed_file: combine2/combined
      tf2_threshold: tf2_threshold
      prefs_bed_file: preference/preferences
    out: [filtered_preferences]
  # change_precision?
  name_output:
    run: cat.cwl
    in:
      input_file: filter/filtered_preferences
      output_filename: output_filename
    out: [output]


