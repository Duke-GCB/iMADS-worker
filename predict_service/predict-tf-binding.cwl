cwlVersion: v1.0
class: CommandLineTool
baseCommand: predict_tf_binding.py
hints:
  DockerRequirement:
    dockerPull: dukegcb/predict-tf-binding
inputs:
  sequence:
    type: File
    inputBinding:
      prefix: -s
  chroms:
    type: string[]?
    inputBinding:
      prefix: --chroms
      itemSeparator: " "
      separate: true
  model:
    type: File[]
    inputBinding:
      prefix: -m
  core:
    type: string[]
    inputBinding:
      prefix: -c
  width:
    type: int
    inputBinding:
      prefix: -w
  kmers:
    type: int[]
    inputBinding:
      prefix: -k
  slope_intercept:
    type: boolean
    default: false
    inputBinding:
      prefix: -i
  skip_size_check:
    type: boolean
    default: true
    inputBinding:
      prefix: --skip-size-check
  transform:
    type: boolean
    default: false
    inputBinding:
      prefix: -t
  core_start:
    type: int?
    inputBinding:
      prefix: --core-start
outputs:
  predictions:
    type: File[]
    outputBinding:
      glob: "predict_output_*.bed"
