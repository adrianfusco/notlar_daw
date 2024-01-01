FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app/

# Expose port 5000 for the Flask app
EXPOSE 5000
