# Use official Python 3.10 slim image
FROM python:3.10-slim

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y ffmpeg gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container
COPY . .

# Collect static files if you need (optional)
# RUN python manage.py collectstatic --noinput

# Expose the port your app runs on (default 8000)
EXPOSE 8000

# Run the Django app with Gunicorn
CMD ["gunicorn", "youtube_jukebox.wsgi:application", "--bind", "0.0.0.0:8000"]
