FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt

# Command to run your Python script
CMD ["python", "main.py"]