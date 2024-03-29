FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive LANG=C TZ=UTC
ENV TERM linux

# install some basic utilities
RUN set -xue ;\
    apt-get update ;\
    apt-get install -y --no-install-recommends \
        build-essential \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libglib2.0-0 \
        wget \
        python3-dev \
        python3-pip \
    ;\
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y libgl1-mesa-glx && apt-get install -y libusb-1.0-0

COPY . /app

# Set working directory inside the container
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your Python script
CMD ["python3", "main.py"]
