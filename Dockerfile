# Use the official Debian 12 (Bookworm) image as a base
FROM python:3.10.13-bookworm

# Set the working directory to /app
WORKDIR /project

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set the environment variable to point to ChromeDriver's path
ENV PATH="/usr/lib/chromium/:$PATH"

COPY requirements.txt requirements.txt

COPY ./project /project

RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port for JupyterLab
EXPOSE 8050

# Run JupyterLab when the container starts
CMD ["python3", "app.py"]