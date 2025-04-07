"""
Setup Module for Dungeon Generator

This module contains the setup configuration for packaging the Dungeon Generator project.
"""

from setuptools import setup, find_packages

setup(
    name="dungeon_generator",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],  # Requirements already handled in requirements.txt
    author="Stewinjo",
    description="Procedural grid-based dungeon generator with UVTT export support.",
    license="Proprietary",
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
