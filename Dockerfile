
# Use the official Python image as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents (including app.py and requirements.txt) into the container at /app
COPY ./python/. /app

# Install Flask (and any other dependencies you list in requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 (the default Flask port)
EXPOSE 5000

# Define the command to run your Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
