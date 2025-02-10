# Use an official Python base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy only required files (helps with caching)
COPY app.py requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for Flask
EXPOSE 5000

# Run Flask using Gunicorn with 1 worker (single process) and multiple threads
CMD ["gunicorn", "-w", "1", "--threads", "4", "-b", "0.0.0.0:5000", "app:app"]