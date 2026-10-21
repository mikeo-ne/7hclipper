from setuptools import setup, find_packages

setup(
    name="7hclipper",
    version="0.1.0",
    description="AI-powered YouTube video clipping and lyric video generation",
    packages=find_packages(),
    install_requires=[
        "yt-dlp",
        "ffmpeg-python",
        "pytube",
    ],
    entry_points={
        "console_scripts": [
            "7hclipper=py7hclipper.__main__:main",
        ],
    },
    python_requires=">=3.8",
)