#!/bin/bash
set -eo pipefail
PYTHONPATH=./package/python python3 function/lambda_function.test.py
