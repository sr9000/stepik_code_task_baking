#!/usr/bin/env bash
python3 run_on_sample.py && \
  python3 run_validation.py && \
  python3 run_build_dataset.py && \
  python3 run_compilation.py && \
  python3 run_validation_my.py