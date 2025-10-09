from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="kfaligner",
    version="0.1.0",
    description="HTK-based Korean forced aligner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="exphon",
    url="https://github.com/exphon/kfaligner",
    packages=find_packages(),
    package_data={
        'kfaligner': [
            'config/*.mfcc',
            'config/*.hvite',
            'config/*.train',
            'config/*.hmm',
        ],
    },
    include_package_data=True,
    install_requires=[
        "numpy>=1.19.0",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="speech-recognition forced-alignment korean htk phoneme",
    entry_points={
        'console_scripts': [
            'kfaligner-prepare=scripts.prepare_data:main',
            'kfaligner-train=scripts.train_models:main',
            'kfaligner-example=scripts.example_usage:main',
        ],
    },
)
