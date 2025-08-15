#!/bin/bash
# Author: Eon (Himanshu Shekhar)
# Created: 2025-08-15
# Description: Test runner script for Kafka Python utility
# License: MIT
# Repository: https://github.com/eonn/kafka-python-kerberos
# Convenience script to run tests with the virtual environment activated.

# Run the specified script or default to test_kerberos_setup.py
if [ $# -eq 0 ]; then
    echo "Running Kerberos setup test..."
    ./venv/bin/python test_kerberos_setup.py
else
    echo "Running $1..."
    ./venv/bin/python "$1"
fi
