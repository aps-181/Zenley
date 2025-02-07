# Use an official Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements.txt first, to leverage Docker's cache
COPY requirements.txt /app/

# Install Python dependencies (if requirements.txt is updated, this step will run)
RUN pip3 install --no-cache-dir -r requirements.txt

# Now, copy the rest of your application files
COPY . /app

# Expose the port if needed (example port 5000 for a web app)
EXPOSE 5000

# Set the default command to run your Python application (if you have one)
CMD ["python", "bot.py"]
