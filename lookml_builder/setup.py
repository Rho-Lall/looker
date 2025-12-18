#!/usr/bin/env python3
"""
Setup script for LookML CLI
"""

from setuptools import setup, find_packages

setup(
    name="lookml-cli",
    version="0.1.0",
    description="LookML CLI tools for generating refinement layers",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "PyYAML>=6.0",
        "lkml>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "lookml=lookml_builder.code.cli:lookml",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)