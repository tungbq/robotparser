# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Define environment variable
ENV PYTHONUNBUFFERED 1

# Run robotparser.py when the container launches
CMD ["python", "robotparser.py"]
