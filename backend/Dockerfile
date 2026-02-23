# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container at /code
COPY ./requirements.txt /code/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the backend application code
COPY ./app /code/app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONPATH=/code

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
