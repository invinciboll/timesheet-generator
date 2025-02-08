# Use the official Python image as a base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install apt-utils and locales to handle locale setup and avoid debconf warnings
RUN apt-get update && \
    apt-get install -y apt-utils locales

RUN sed -i '/de_DE.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

ENV LANG de_DE.UTF-8
ENV LANGUAGE de_DE:de
ENV LC_ALL de_DE.UTF-8

RUN update-locale LANG=de_DE.UTF-8

# Install pdf tool wkhtmltopdf
RUN apt-get update && \
    apt-get install -y wkhtmltopdf

# Create and set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Define the command to run the Flask app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5111", "app:app"]
