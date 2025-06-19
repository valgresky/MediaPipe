FROM runpod/base:0.4.0-cpu

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy handler
COPY handler.py .
COPY measurement_utils.py .

# RunPod handler
CMD ["python3", "-u", "handler.py"]
