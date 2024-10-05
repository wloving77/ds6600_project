# Use the official Debian 12 (Bookworm) image as a base
FROM python:3.10.13-bookworm

# Set the working directory to /app
WORKDIR /project

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Expose the port for JupyterLab
EXPOSE 8888

# Run JupyterLab when the container starts
CMD ["jupyter", "lab", "--allow-root", "--ip=0.0.0.0", "--port=8888"]