from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="focussentinel-ai",
    version="1.0.0",
    author="Usama Baig",
    author_email="mearoobmughal@gmail.com",
    description="Intelligent Vision-based Micro-Sleep & Attention Proctoring Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ononymuos/FocusSentinel-AI",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Video :: Capture",
    ],
    python_requires=">=3.9",
    install_requires=[
        "opencv-python>=4.8.0",
        "cvzone>=2.0.0",
        "ultralytics>=8.0.0",
        "pygame>=2.5.0",
        "mediapipe>=0.10.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "focussentinel=main:main",
        ],
    },
)
