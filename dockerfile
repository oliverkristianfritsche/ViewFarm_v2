# Use the official NVIDIA CUDA runtime as a parent image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

# Set the working directory in the container
WORKDIR /root

# Install dependencies, Python 3.11, and FFmpeg with NVIDIA support
RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    wget \
    build-essential \
    libsndfile1 \
    git \
    curl \
    libsm6 \
    libxext6 \
    libxrender1 \
    libx264-dev \
    libx265-dev \
    libnuma-dev \
    libfdk-aac-dev \
    libmp3lame-dev \
    libopus-dev \
    pkg-config \
    yasm \
    nasm \
    libfreetype6-dev \
    libfontconfig1 \
    imagemagick && \
    apt-get clean

# Install ffmpeg with NVENC support
RUN apt-get install -y ffmpeg

# Manually install pip for Python 3.11
RUN wget https://bootstrap.pypa.io/get-pip.py && python3.11 get-pip.py && rm get-pip.py

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install Python packages from requirements.txt
RUN python3.11 -m pip install -r requirements.txt

# Ensure the NVIDIA driver files are available
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,video,utility

# Default command
CMD ["python3.11", "main.py"]
