# Use an official Python runtime as a parent image.
# The 'slim' version is smaller and good for production.
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /code

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies that might be needed by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies.
# Using --no-cache-dir makes the image smaller.
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Download the model during the build process
COPY download_model.py .
RUN python download_model.py

# Copy the application code (the 'app' directory) into the container
COPY ./app ./app

# Expose the port that the Uvicorn server will run on
EXPOSE 8080

# The command to run the application when the container starts.
# We use 0.0.0.0 to make the server accessible from outside the container.
# The --host and --port flags are for production, not development.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
