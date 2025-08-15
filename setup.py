#!/usr/bin/env python3
"""
Setup script for Kafka Kerberos Utility

Author: Eon (Himanshu Shekhar)
Created: 2025-08-15
Description: Setup script for Kafka Python utility with Kerberos
License: MIT
Repository: https://github.com/eonn/kafka-python-kerberos

This script allows the utility to be installed as a Python package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    """Read README.md file."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Kafka Python Utility with Kerberos Authentication"

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file."""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="kafka-kerberos-utility",
    version="1.0.0",
    author="Eon (Himanshu Shekhar)",
    author_email="eon@example.com",
    description="A comprehensive Python utility for Apache Kafka with Kerberos authentication",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/eonn/kafka-python-kerberos",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "kafka-kerberos-utility=kafka_kerberos_utility:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="kafka kerberos authentication gssapi sasl messaging",
    project_urls={
        "Bug Reports": "https://github.com/eonn/kafka-python-kerberos/issues",
        "Source": "https://github.com/eonn/kafka-python-kerberos",
        "Documentation": "https://github.com/eonn/kafka-python-kerberos#readme",
    },
)
